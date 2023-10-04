# Open FPGA control sub-project for Fluorescence Activated (Microfluidic) Droplet Sorting (FADS) [![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

This repository addresses an aspect of microfluidic droplet sorting: The real-time computation solution for fluorescnece signal analysis, based on a FPGA-chip, here on board a small affordable computer with web-server, the [RedPitaya](https://github.com/RedPitaya). For a more general discussion of Fluorescence Activated (Microfluidic) Droplet Sorting (FADS), see the [Open Microfluidics repository](https://github.com/MakerTobey/OpenMicrofluidics/tree/master/Open%20Fluorescence%20Activated%20Droplet%20Sorting%20(FADS)), with emphasis on the measurement hardware. FADS is the keystone method of *high-throughput droplet microfluidic* biological assays.

Follow us! [#twitter](https://twitter.com/WenzelLab), [#YouTube](https://www.youtube.com/@librehub), [#LinkedIn](https://www.linkedin.com/company/92802424), [#instagram](https://www.instagram.com/wenzellab/), [#Printables](https://www.printables.com/@WenzelLab), [#LIBREhub website](https://librehub.github.io), [#IIBM website](https://ingenieriabiologicaymedica.uc.cl/en/people/faculty/821-tobias-wenzel)

## Background

Approach and platform choice

The overaching aim of this project is to *open up* microfluidic experimentation, by creating a prototype instrument that is based on *connectable*, *open source hardware*, modern and *low-cost* components (such as RasberriPi, Adrunio, 3D printing, on-board components, open or at least accessible design software and operation software especially python). A key design element for this purpose is that the hardware and sorftware design is *easy to understand and modify for most interested scientists*, in contrast to many efforts in current Open Source FPGA development, which need substantive developer expertise. Currently, similar solutions in the lab come either in a "black-box instrument" as a commercial closed-source and non-modyfiable solution, or are assembled by scientists based on National Instruments FPGA cards with user-friendly yet obscure, expensive and closed-source LabView software libraries. Both solutions are not satisfying for the budget or modifyability of most academic labs in the world.

After much consideration, we chose to base our development on the [RedPitaya](https://github.com/RedPitaya) computer board. Even though the FPGA chip itself and the compilation software of the Verilog code to program the FPGA are NOT Open Source, the RedPitaya board design is Open Source and cultivates an extensive academia-development-targeted Open Source software and tutorial framework. The board (here STEMlab 125-14) can also be purchased for ca. 300$ and contains a full linux computer with webserver, similar to the popular (non-FPGA) RasperriPi computer. Most importantly, it has two fast analogue input and output ports that are needed for droplet signal detection and sorting triggering. It is therefore a very accessible starting point. We have based our actual FPGA coding on the Open Source Python library [pyrpl](http://lneuhaus.github.io/pyrpl/).

Note, the [RedPitaya](https://github.com/RedPitaya) now has an X-Channel product where single board computers can be stacked to expand the number of analogue input and output channels. We already have a 6-input channel version now and will soon be looking to adjust the software to work with 6 sensors in parallel.

## Usage

The documentation of work on this project can be found on this repositorie's [wiki](https://github.com/wenzel-lab/droplet-sorting-FPGA-controller/wiki).

It contains:

** A description of our [development environment](https://github.com/wenzel-lab/droplet-sorting-FPGA-control/wiki/Development-Environment), 

** Detail on the [workflow](https://github.com/wenzel-lab/droplet-sorting-FPGA-control/wiki/Development-Workflow) for FADS including the Verilog code for the sorting trigger,

** A [first GUI architecture](https://github.com/wenzel-lab/droplet-sorting-FPGA-control/wiki/GUI-Architecture) to look at signals and results,

** And detail on [memory access](https://github.com/wenzel-lab/droplet-sorting-FPGA-control/wiki/Memory-Access) - how to save results back into the memory of the main computer for web-server access.

## Contribute

You're free to fork the project and enhance it. If you have any suggestions to improve it or add any additional functions make a pull-request or [open an issue](https://github.com/wenzel-lab/droplet-sorting-FPGA-control/issues/new).
For interactions in our team and with the community applies the [GOSH Code of Conduct](https://openhardware.science/gosh-2017/gosh-code-of-conduct/).

We would be particularly excited about extensions such as: Simplify the pyprl library fork to the needed tools in this context; further development of the GUI for the user/experimentor and to change the sorting parameters; collecting custom droplet sorting challenges not currently well addressed by exsisting literature examples; extension to more-dimensional questions (boards with more fast analougue inputs-outputs, sorting based on spectral analysis with detector array, sorting based on 2D detector arrays such as imaging detectors, sorting with additional sensor to verify positive sorting events, etc.).

## License

[CERN OHL 2W](LICENSE) © Nicolas Peschke and Tobias Wenzel. This project is Open Source Hardware - please acknowledge us when using the hardware or sharing modifications.
