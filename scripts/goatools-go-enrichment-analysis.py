import pandas as pd
from goatools.obo_parser import GODag
from goatools.anno.idtogos_reader import IdToGosReader
from goatools.goea.go_enrichment_ns import GOEnrichmentStudyNS
from goatools.godag_plot import plot_results#, plot_goid2goobj, plot_gos


# read in directed acyclic graph of GO terms / IDs
obodag = GODag(snakemake.input.obo)


# read in mapping gene ids from input to GO terms / IDs
objanno = IdToGosReader(snakemake.input.ens_gene_to_go, godag = obodag)


# extract namespace(?) -> id2gos mapping
ns2assoc = objanno.get_ns2assc()

for nspc, id2gos in ns2assoc.items():
    print("{NS} {N:,} annotated mouse genes".format(NS=nspc, N=len(id2gos)))


# read gene diffexp table
all_genes = pd.read_table(snakemake.input.diffexp)

# select genes significantly differentially expressed according to BH FDR of sleuth
sig_genes = all_genes[all_genes['qval']<0.01]


# initialize GOEA object

goeaobj = GOEnrichmentStudyNS(
    # list of 'population' of genes looked at in total
    pop = all_genes['ens_gene'].tolist(), 
    # geneid -> GO ID mapping
    ns2assoc = ns2assoc, 
    # ontology DAG
    godag = obodag, 
    propagate_counts = False,
    # multiple testing correction method (fdr_bh is false discovery rate control with Benjamini-Hochberg)
    methods = ['fdr_bh'],
    # standard significance cutoff for what?
    alpha = 0.05
    )

goea_results_all = goeaobj.run_study(sig_genes['ens_gene'].tolist())


# write results to text file
goeaobj.wr_tsv(snakemake.output.enrichment, goea_results_all)


# plot results
ensembl_id_to_symbol = dict(zip(all_genes['ens_gene'], all_genes['ext_gene']))


# from first plot output file name, create generic file name to trigger
# separate plots for each of the gene ontology name spaces
outplot_generic = snakemake.output.plot[0].replace('_BP.','_{NS}.', 1).replace('_CC.','_{NS}.', 1).replace('_MF.', '_{NS}.', 1)
goea_results_sig = [r for r in goea_results_all if r.p_fdr_bh < 0.05]

plot_results(
    outplot_generic,
    # use pvals for coloring
    goea_results=goea_results_sig,
    # print general gene symbol instead of Ensembl ID
    id2symbol=ensembl_id_to_symbol, 
    # number of genes to print, or True for printing all (including count of genes)
    study_items=True,
    # number of genes to print per line
    items_p_line=6,
    # p-values to use for coloring of GO term nodes (argument name determined from code and testing against value "p_uncorrected")
    pval_name="p_fdr_bh"
    )

