import rdf.rdf as rdf
import pathlib as pl

import plugy.data.pmt as pmt

import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == '__main__':
    sns.set_style("darkgrid")

    data_dir = pl.Path("data/droplet_test_acq_2020-02-21")

    left_border = 145.01
    right_border = 145.08

    pmt_data = pmt.PmtData(data_dir.joinpath("recording_green_02_100kHz_1.txt.gz"),
                           acquisition_rate=100000)

    pmt_overview_fig, pmt_overview_ax = plt.subplots(1, 1, figsize=(150, 10))
    pmt_data.plot_pmt_data(pmt_overview_ax)

    pmt_overview_ax.set_ylim(bottom=0, top=0.1)
    pmt_overview_ax.axvline(left_border)
    pmt_overview_ax.axvline(right_border)

    pmt_overview_fig.tight_layout()
    pmt_overview_fig.show()

    raw_sequence = pmt_data.cut_data(cut=(left_border, right_border)).iloc[:rdf.RDF.DATA_LENGTH]
    raw_sequence = raw_sequence[["green", "orange", "uv"]].max(axis=1)

    rdf_sequence = rdf.RDF(raw_sequence)
    rdf_sequence.save(data_dir.joinpath("normal_droplet.rdf"))
