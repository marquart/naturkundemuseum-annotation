from SemanticModels import SemanticEntity, SemanticProperty, SemanticData

if __name__ == "__main__":
    pickle_file = "../Data/ParsedSemanticAnnotations.pickle"
    
    data = SemanticData(pickle_file)

    for e in data.entities:
        if e.year == 1899 and ("pisces" in e.search_string or "fisch" in e.search_string):
            print(e.id, e)
            for r in e.incoming: print("    ", r, r.source.id)
            print('\n')
            for r in e.outgoing: print("    ", r, r.target.id)
