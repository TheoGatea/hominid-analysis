from typing import List
from typedefs import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
            capacities = [hm.cranial_cap for hm in self.hominids if hm.species == sp]
            plt.hist(capacities, label=sp, alpha=0.5)
        plt.legend()
        plt.show()

    def disp_skull_body_correlation(self) -> None:
        skull_caps = [hm.cranial_cap for hm in self.hominids]
        height = [hm.height for hm in self.hominids]
        fig = plt.figure()
        ax1, ax2 = fig.add_subplot(2, 1, 1), fig.add_subplot(2, 1, 2)
        ax1.scatter(height, skull_caps)
        ax1.set_xlabel("height")
        ax1.set_ylabel("skull capacity")

        # dont know if useful
        # ht_sk_pairs = np.column_stack((height, skull_caps))
        # real_r = np.corrcoef(height, skull_caps)[0, 1]
        # bs_n, bs_r = 1000, []
        # for _ in range(bs_n):
        #     ht_sk_bs = ht_sk_pairs[np.random.choice(len(ht_sk_pairs), size=len(ht_sk_pairs))]
        #     bs_ht , bs_sk = ht_sk_bs[:, 0], ht_sk_bs[:, 1]
        #     r = np.corrcoef(bs_ht, bs_sk)[0, 1]
        #     bs_r.append(r)
        # ax2.hist(bs_r)
        # ax2.axvline(real_r, color='g')
        plt.show()


def disp_help(opts: List[str]) -> None:
    print("This is the plotting console. Choose a possible plot to view or enter exit or quit to stop.")
    print("These are the options:")
    for o in opts:
        print(o)


if __name__ == "__main__":
    context = DataContext("evolution_data.csv")
    display_options = ["skull bar chart", "skull distribution", "skull to body scatter"]
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
            case "help":
                disp_help(display_options)
            case "exit" | "quit":
                exit(0)
            case _:
                print("not a possible command")


