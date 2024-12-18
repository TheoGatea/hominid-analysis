from typing import List
from typedefs import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import shapiro, kstest, kruskal, norm, spearmanr, linregress, percentileofscore
import scikit_posthocs as sp

class DataContext:
    def __init__(self, db_filename: str) -> None:
        data = pd.read_csv(db_filename)
        hominid_lst = []
        for nm, cran_cap, ht, tech_yn, techtp, diettp in \
                zip(list(data["Genus_&_Specie"]),
                    list(data["Cranial_Capacity"]),
                    list(data["Height"]), list(data["Tecno"]),
                    list(data["Tecno_type"]), list(data["Diet"])):
                        tech_flag = False
                        match tech_yn:
                            case "yes":
                                tech_flag = True
                            case "no":
                                tech_flag = False
                            case "likely":
                                tech_flag = True
                            case _:
                                raise NotImplementedError(f"no such tech flag {tech_yn}")
                        tech_type = TechType.from_str(techtp) if tech_flag else TechType.NO_TECH 
                        diet_type = DietType.from_str(diettp)
                        current_hom = Hominid(nm, float(cran_cap), float(ht), \
                                    tech_type, diet_type, float(cran_cap) / float(ht))
                        hominid_lst.append(current_hom)
        self.hominids = hominid_lst
        self.raw_data = data


    def disp_skull_barchart(self) -> None:
        all_species = list(set([hm.species for hm in self.hominids]))
        cranium_means = [np.mean([hm.cranial_cap for hm in self.hominids if hm.species == sp]) for sp in all_species]
        cranium_std = [np.std([hm.cranial_cap for hm in self.hominids if hm.species == sp]) for sp in all_species]
        plt.bar(all_species, cranium_means, yerr=cranium_std)
        plt.xticks(rotation='vertical')
        plt.show()

    def disp_skull_dist(self) -> None:
        all_species = list(set([hm.species for hm in self.hominids]))
        for sp in all_species:
            capacities = [hm.skull_body_ratio for hm in self.hominids if hm.species == sp]
            plt.hist(capacities, label=sp, alpha=0.5)
        plt.legend()
        plt.show()

    def disp_skull_body_correlation(self) -> None:
        skull_caps = [hm.cranial_cap for hm in self.hominids]
        height = [hm.height for hm in self.hominids]
        model = linregress(height, skull_caps)
        k, slope = model.intercept, model.slope
        plt.scatter(height, skull_caps)
        plt.plot(height, k + slope * np.array(height), color='r')
        plt.xlabel("height")
        plt.ylabel("skull capacity")
        plt.text(0.02, 0.5, f"r^2 = {model.rvalue**2:.2f}", fontsize=14, transform=plt.gcf().transFigure)
        plt.show()


    def disp_sbr_tech_boxplot(self) -> None:
        """
        Displays a boxplot of skull-body ratios for each tech_type.
        """
        all_tecnos = [TechType.NO_TECH, TechType.PRIMITIVE, TechType.M_1, TechType.M_2, TechType.M_3, TechType.M_4]
        grouped_sbrs = [[hm.skull_body_ratio for hm in self.hominids if hm.tech_type == tc] for tc in all_tecnos]
        labels = [t.to_string() for t in all_tecnos]
        
        # plot
        plt.figure(figsize=(10, 6))
        plt.boxplot(grouped_sbrs, tick_labels=labels, vert=True, patch_artist=True)
        plt.title("Skull to Body Ratios by Tech Type")
        plt.xlabel("Tech Type")
        plt.ylabel("Skull-Body Ratio")
        plt.show()

    def disp_sbr_dist(self) -> None:
        all_tecnos = list(set([hm.tech_type for hm in self.hominids]))
        for tc in all_tecnos:
            sbrs = [hm.skull_body_ratio for hm in self.hominids if hm.tech_type == tc]
            plt.hist(sbrs, label=tc, alpha=0.5)
        plt.legend()
        plt.show()


    def kolmogorov_smirnov(self) -> None:
        all_species = list(set([hm.species for hm in self.hominids]))
        for sp in all_species:
            ratios = [hm.skull_body_ratio for hm in self.hominids if hm.species == sp]
            mean, stdev = np.mean(ratios), np.std(ratios)
            n = len(ratios)
            ks_max = np.sqrt(- np.log(0.05 / 2) * (2 / (2 * n)))
            (ks_stat, _) = kstest(ratios, "norm", args=(mean, stdev))
            bstraps = [kstest(np.random.choice(ratios, size=n), "norm", args=(mean, stdev))[0] for _ in range(1000)]
            print(f"{sp}: {ks_stat} p = {percentileofscore(bstraps, ks_stat) / 100 * 2}")
            if ks_stat > ks_max:
                print(f"    KS-statistic too big, {ks_stat} > {ks_max}")


    def plot_ecdf(self) -> None:
        species = 'hominino Orrorin tugenencin'
        ratios = list(set([hm.skull_body_ratio for hm in self.hominids if hm.species == species]))
        mean, stdev = np.mean(ratios), np.std(ratios)
        
        # generate the ECDF for the observed data
        ratios_sorted = np.sort(ratios)
        ecdf = np.arange(1, len(ratios) + 1) / len(ratios)
        
        # generate the normal CDF
        x_vals = np.linspace(min(ratios_sorted), max(ratios_sorted), 1000)
        normal_cdf = norm.cdf(x_vals, loc=mean, scale=stdev)
        ks_index = np.argmax(np.abs(ecdf - norm.cdf(ratios_sorted, loc=mean, scale=stdev)))

        plt.plot(ratios_sorted, ecdf, label="Empirical CDF", marker='o', linestyle='none', markersize=3)
        plt.plot(x_vals, normal_cdf, label="Normal CDF", color='red', lw=2)
        plt.vlines(ratios_sorted[ks_index], ecdf[ks_index], norm.cdf(ratios_sorted[ks_index], loc=mean, scale=stdev), 
                    color="red", linestyle="--", label="KS Stat")
        plt.title(f"KS Test for {species}")
        plt.xlabel("Skull-Body Ratio")
        plt.ylabel("Cumulative Probability")
        plt.legend()
        plt.grid()
        plt.show()

    def shapiro_wilk(self) -> None:
        all_species = list(set([hm.species for hm in self.hominids]))
        for sp in all_species:
            ratios = [hm.skull_body_ratio for hm in self.hominids if hm.species == sp]
            (shp_stat, p) = shapiro(ratios)
            print(f"{sp}: {shp_stat}, {p}")
            

    def kruskal_wallis_techno(self) -> None:
        """Performs Kruskal-Wallis test between sbrs of humans classified by technology types."""
        all_tecnos = [TechType.NO_TECH, TechType.PRIMITIVE, TechType.M_1, TechType.M_2, TechType.M_3, TechType.M_4]
        ratios = [[hm.skull_body_ratio for hm in self.hominids if hm.tech_type == tc] for tc in all_tecnos]
        only_tech_r = [[hm.skull_body_ratio for hm in self.hominids if hm.tech_type == tc] for tc in all_tecnos[2:]]
        (h_stat, p) = kruskal(*only_tech_r)
        print(f"For individuals who have achieved greater than primitive tech H = {h_stat}, p = {p}")
        (h_stat, p) = kruskal(*ratios)
        print(f"Kruskal-Wallis H-stat: {h_stat}, p-value: {p}")
        if p < 0.05:
        
            data = []
            for tecno, ratio_list in zip(all_tecnos, ratios):
                data.extend([(tecno, ratio) for ratio in ratio_list])
        
            df = pd.DataFrame(data, columns=["Technology", "Skull_to_Body_Ratio"])
        
        
            posthoc = sp.posthoc_dunn(df, val_col="Skull_to_Body_Ratio", group_col="Technology", p_adjust="bonferroni")
            print("Post Hoc Dunn's Test Results:")
            print(posthoc)
        else:
            print("No significant differences detected; post hoc analysis not performed.")
        technology_encoded = []
        skull_to_body_ratios = []
    
        for i, tc in enumerate(all_tecnos):
            technology_encoded.extend([i] * len(ratios[i]))  
            skull_to_body_ratios.extend(ratios[i])
    
   
        spearman_corr, spearman_p = spearmanr(technology_encoded, skull_to_body_ratios)
        print(f"Spearman correlation: {spearman_corr}, p-value: {spearman_p}")

def disp_help(opts: List[str]) -> None:
    print("This is the plotting console. Choose a possible plot to view or enter exit or quit to stop.")
    print("These are the options:")
    for o in opts:
        print(o)

if __name__ == "__main__":
    context = DataContext("evolution_data.csv")
    display_options = ["skull bar chart", "skull distribution", "skull to body scatter",
                       "sbr/technology boxplot", "sbr distribution", "ks test", "ecdf plot", "shapiro wilk test",
                       "kw tech type"]
    disp_help(display_options)
    while True:
        try:
            cmd = input("> ")
        except (EOFError, KeyboardInterrupt):
            exit(0)                        
        match cmd:
            case "skull bar chart":
                context.disp_skull_barchart()
            case "skull distribution":
                context.disp_skull_dist()
            case "skull to body scatter":
                context.disp_skull_body_correlation()
            case "sbr/technology boxplot":
                context.disp_sbr_tech_boxplot()
            case "sbr distribution":
                context.disp_sbr_dist()
            case "ks test":
                context.kolmogorov_smirnov()
            case "ecdf plot":
                context.plot_ecdf()
            case "shapiro wilk test":
                context.shapiro_wilk()
            case "kw tech type":
                context.kruskal_wallis_techno()
            case "help":
                disp_help(display_options)
            case "exit" | "quit":
                exit(0)
            case _:
                print("not a possible command")


