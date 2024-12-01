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


def disp_skull_barchart(ctx: DataContext) -> None:
    all_species = list(set([hm.species for hm in ctx.hominids]))
    cranium_means = [np.mean([hm.cranial_cap for hm in ctx.hominids if hm.species == sp]) for sp in all_species]
    cranium_std = [np.std([hm.cranial_cap for hm in ctx.hominids if hm.species == sp]) for sp in all_species]
    plt.bar(all_species, cranium_means, yerr=cranium_std)
    plt.xticks(rotation='vertical')
    plt.show()

def disp_skull_dist(ctx: DataContext) -> None:
    all_species = list(set([hm.species for hm in ctx.hominids]))
    for sp in all_species:
        capacities = [hm.cranial_cap for hm in ctx.hominids if hm.species == sp]
        plt.hist(capacities, label=sp, alpha=0.5)
    plt.legend()
    plt.show()

def disp_skull_body_scatter(ctx: DataContext) -> None:
    skull_caps = [hm.cranial_cap for hm in ctx.hominids]
    height = [hm.height for hm in ctx.hominids]
    plt.scatter(height, skull_caps)
    plt.xlabel("height")
    plt.ylabel("skull capacity")
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
                disp_skull_barchart(context)
            case "skull distribution":
                disp_skull_dist(context)
            case "skull to body scatter":
                disp_skull_body_scatter(context)
            case "help":
                disp_help(display_options)
            case "exit" | "quit":
                exit(0)
            case _:
                print("not a possible command")


