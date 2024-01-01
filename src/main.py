import os
import pandas

from cooc import Cooc, BookType

def main() -> None:
    # charge les fichiers texte
    path_paf = "res/corpus_asimov_leaderboard_normalized/prelude_a_fondation_normalized"
    texts_paf: list[str] = os.listdir(path_paf)
    texts_paf_fixed: list[str] = []
    for name in texts_paf:
        # enlève l'extension .txt
        texts_paf_fixed.append(os.path.splitext(name)[0])

    texts_paf = texts_paf_fixed

    path_lca = "res/corpus_asimov_leaderboard_normalized/les_cavernes_d_acier_normalized"
    texts_lca: list[str] = os.listdir(path_lca)
    texts_lca_fixed: list[str] = []
    for name in texts_lca:
        texts_lca_fixed.append(os.path.splitext(name)[0])

    texts_lca = texts_lca_fixed

    # charge les lexiques
    lexicons_paf: list[str] = os.listdir("res/corpus_asimov_leaderboard_REN/prelude_a_fondation_REN")
    lexicons_paf_fixed: list[str] = []
    for name in lexicons_paf:
        lexicons_paf_fixed.append(os.path.splitext(name)[0])

    lexicons_paf = lexicons_paf_fixed

    lexicons_lca: list[str] = os.listdir("res/corpus_asimov_leaderboard_REN/les_cavernes_d_acier_REN")
    lexicons_lca_fixed: list[str] = []
    for name in lexicons_lca:
        lexicons_lca_fixed.append(os.path.splitext(name)[0])

    lexicons_lca = lexicons_lca_fixed

    # prépare la soumission
    df_submit = {"ID": [], "graphml": []}

    ## PAF
    for chap in texts_paf:
        chap_lexicon: str = f"res/corpus_asimov_leaderboard_REN/prelude_a_fondation_REN/{chap}.json"
        chap_text: str = f"res/corpus_asimov_leaderboard_normalized/prelude_a_fondation_normalized/{chap}.txt"

        cooc: Cooc = Cooc(chap_lexicon, chap_text, BookType.PAF, int(chap) - 1)
        bid, graph = cooc.find()
        df_submit["ID"].append(bid)
        df_submit["graphml"].append(graph)

    ## LCA
    for chap in texts_lca:
        chap_lexicon: str = f"res/corpus_asimov_leaderboard_REN/les_cavernes_d_acier_REN/{chap}.json"
        chap_text: str = f"res/corpus_asimov_leaderboard_normalized/les_cavernes_d_acier_normalized/{chap}.txt"

        cooc = Cooc(chap_lexicon, chap_text, BookType.LCA, int(chap) - 1)
        bid, graph = cooc.find() 
        df_submit["ID"].append(bid)
        df_submit["graphml"].append(graph)

    df = pandas.DataFrame(df_submit)
    df.set_index("ID", inplace=True)
    df.to_csv("./my_submission.csv")

if __name__ == "__main__":
    main()
