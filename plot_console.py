from typing import List
from typedefs import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ks_1samp, shapiro, kstest, kruskal, norm
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
                        tech_type = TechType.from_str(techtp) if tech_flag else None
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
        plt.scatter(height, skull_caps)
        plt.xlabel("height")
        plt.ylabel("skull capacity")
        plt.show()

    def group_tecno_sbr(self):
        """
        Groups skull-body ratios by tech_type.
        Returns a tuple of all tech types and their corresponding grouped skull-body ratios.
        """
        all_tecnos = list(set([hm.tech_type for hm in self.hominids]))
        grouped_sbrs = [[hm.skull_body_ratio for hm in self.hominids if hm.tech_type == tc] for tc in all_tecnos]
        return all_tecnos, grouped_sbrs

    def disp_sbr_tech_boxplot(self):
        """
        Displays a boxplot of skull-body ratios for each tech_type.
        """
        all_tecnos, grouped_sbrs = self.group_tecno_sbr()
        
        # plot
        plt.figure(figsize=(10, 6))
        plt.boxplot(grouped_sbrs, tick_labels=all_tecnos, vert=True, patch_artist=True)
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
            dist = np.random.normal(mean, stdev, len(ratios))
            # do both
            (ks_stat, _) = kstest(ratios, "norm", args=(mean, stdev))
            ks_max = np.sqrt(- np.log(0.05 / 2) * (2 / (2 * len(ratios))))
            print(f"{sp}: {ks_stat} {ks_max}")


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
        all_tecnos, ratios = self.group_tecno_sbr()
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

def disp_help(opts: List[str]) -> None:
    print("This is the plotting console. Choose a possible plot to view or enter exit or quit to stop.")
    print("These are the options:")
    for o in opts:
        print(o)

if __name__ == "__main__":
    context = DataContext("evolution_data.csv")
    display_options = ["skull bar chart", "skull distribution", "skull to body scatter",
                       "sbr/technology boxplot", "sbr distribution", "ks test", "ecdf plot", "shapiro wilk test",
                       "kw species", "kw tech type"]
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
            case "kw species":
                context.kruskal_wallis_spec2()
            case "kw tech type":
                context.kruskal_wallis_techno()
            case "help":
                disp_help(display_options)
            case "exit" | "quit":
                exit(0)
            case _:
                print("not a possible command")


