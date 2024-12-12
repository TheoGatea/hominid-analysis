    def kruskal_wallis_species(self) -> None:
        sbr_per_species = {} # create dictionary
        for hm in self.hominids:
            species = hm.species
            if species not in sbr_per_species:
                sbr_per_species[species] = []
            sbr_per_species[species].append(hm.skull_body_ratio)
        ratios = list(sbr_per_species.values())
        (h_stat, p) = kruskal(*ratios)
        print(f"Kruskal-Wallis H-stat: {h_stat}, p-value: {p}")

    def kruskal_wallis_spec2(self) -> None:
        """Performs KW test between sbrs of human species within the same technology category"""
        all_tecnos = list(set([hm.tech_type for hm in self.hominids]))
        for tc in all_tecnos:
            sbr_per_species = {}
            for hm in self.hominids:
                if hm.tech_type == tc:  # only take current techno type
                    species = hm.species
                    if species not in sbr_per_species:
                        sbr_per_species[species] = []
                    sbr_per_species[species].append(hm.skull_body_ratio)

            # no kw test if not enough species in category
            if len(sbr_per_species) < 2:
                print(f"Not enough species within technology type {tc} for Kruskal-Wallis test.")
                print("-" * 40)
                continue

            ratios = list(sbr_per_species.values())
            species_names = list(sbr_per_species.keys())

            (h_stat, p) = kruskal(*ratios)
            print(f"Technology Type: {tc}")
            print(f"Species compared: {species_names}")
            print(f"Kruskal-Wallis H-stat: {h_stat}, p-value: {p}")
            print("-" * 40)
