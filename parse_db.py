from typedefs import *
import pandas as pd

class DataContext:
    def __init__(self, db_filename: str) -> None:
        data = pd.read_csv(db_filename)
        hominid_lst = []
        for nm, cran_cap, ln, tech_yn, techtp, diettp in \
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
                        tech_type = TechType.from_str(techtp) if tech_flag else None
                        diet_type = DietType.from_str(diettp)
                        current_hom = Hominid(nm, float(cran_cap), float(ln), \
                                    tech_flag, tech_type, diet_type, float(cran_cap) / float(ln))
                        hominid_lst.append(current_hom)
        self.hominids = hominid_lst
        self.raw_data = data


ctx = DataContext("evolution_data.csv")
