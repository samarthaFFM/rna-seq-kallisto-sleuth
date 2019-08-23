include: "rules/common.smk"
include: "rules/trim.smk"
include: "rules/quant.smk"
include: "rules/diffexp.smk"
include: "rules/enrichment.smk"

rule all:
    input:
        expand(
            [
                "tables/diffexp/{model}.transcripts.diffexp.tsv",
                "plots/diffexp-heatmap/{model}.diffexp-heatmap.pdf",
                "tables/tpm-matrix/{model}.tpm-matrix.tsv",
                "tables/pathways/{model}.pathways.tsv",
                "tables/go_terms/{model}.genes-mostsigtrans.diffexp.go_term_enrichment.tsv"
            ],
            model=config["diffexp"]["models"]
        ),
        expand("plots/go_terms/{model}.genes-mostsigtrans.diffexp.go_term_enrichment_{go_ns}.pdf",
            model=config["diffexp"]["models"],
            go_ns=["BP", "CC", "MF"]
        ),
        expand("plots/diffexp/{model}.{level}.diffexp-pval-hist.pdf",
                model=config["diffexp"]["models"],
                level=["transcripts", "genes-aggregated", "genes-mostsigtrans" ]
        ),
        expand("plots/pca/{covariate}.pca.pdf", covariate=samples.columns[samples.columns != "sample"]),
        [get_bootstrap_plots(model) for model in config["diffexp"]["models"]],
        [get_bootstrap_plots(model, config["bootstrap_plots"]["genes_of_interest"])
            for model in config["diffexp"]["models"] ],
        expand("plots/fld/{unit.sample}-{unit.unit}.fragment-length-dist.pdf", unit=units[["sample", "unit"]].itertuples())
