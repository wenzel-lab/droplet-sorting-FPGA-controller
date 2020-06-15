# Open FPGA control sub-project for Fluorescence Activated (Microfluidic) Droplet Sorting (FADS)

This repository addresses an aspect of microfluidic droplet sorting: The real-time computation solution for fluorescnece signal analysis, based on a FPGA-chip, here on board a small affordable computer with web-server, the [RedPitaya](https://github.com/RedPitaya). For a more general discussion of Fluorescence Activated (Microfluidic) Droplet Sorting (FADS), see the [Open Microfluidics repository](https://github.com/MakerTobey/OpenMicrofluidics/tree/master/Open%20Fluorescence%20Activated%20Droplet%20Sorting%20(FADS)), with emphasis on the measurement hardware. FADS is the keystone method of *high-throughput droplet microfluidic* biological assays.


## Approach and platform choice

The overaching aim of this project is to *open up* microfluidic experimentation, by creating a prototype instrument that is based on *connectable*, *open source hardware*, modern and *low-cost* components (such as RasberriPi, Adrunio, 3D printing, on-board components, open or at least accessible design software and operation software especially python). A key design element for this purpose is that the hardware and sorftware design is *easy to understand and modify for most interested scientists*, in contrast to many efforts in current Open Source FPGA development, which need substantive developer expertise. Currently, similar solutions in the lab come either in a "black-box instrument" as a commercial closed-source and non-modyfiable solution, or are assembled by scientists based on National Instruments FPGA cards with user-friendly yet obscure, expensive and closed-source LabView software libraries. Both solutions are not satisfying for the budget or modifyability of most academic labs in the world.

After much consideration, we chose to base our development on the [RedPitaya](https://github.com/RedPitaya) computer board. Even though the FPGA chip itself and the compilation software of the Verilog code to program the FPGA are NOT Open Source, the RedPitaya board design is Open Source and cultivates an extensive academia-development-targeted Open Source software and tutorial framework. The board (here STEMlab 125-14) can also be purchased for ca. 300$ and contains a full linux computer with webserver, similar to the popular (non-FPGA) RasperriPi computer. Most importantly, it has two fast analogue input and output ports that are needed for droplet signal detection and sorting triggering. It is therefore a very accessible starting point. We have based our actual FPGA coding on the Open Source Python library [pyrpl](http://lneuhaus.github.io/pyrpl/).


## Documentation

The documentation of work on this project can be found on this repositorie's [wiki](https://github.com/MakerTobey/Open_FPGA_control_for_FADS/wiki).

It contains:

** A description of our [development environment](https://github.com/MakerTobey/Open_FPGA_control_for_FADS/wiki/Development-Environment), 

** Detail on the [workflow](https://github.com/MakerTobey/Open_FPGA_control_for_FADS/wiki/Development-Workflow) for FADS including the Verilog code for the sorting trigger,

** A [first GUI architecture](https://github.com/MakerTobey/Open_FPGA_control_for_FADS/wiki/GUI-Architecture) to look at signals and results,

** And detail on [memory access](https://github.com/MakerTobey/Open_FPGA_control_for_FADS/wiki/Memory-Access) - how to save results back into the memory of the main computer for web-server access.


## Contribution guide

This is an open collaborative project currently advanced by Nicolas Peschke and me; *your participation* (comments, inputs, contributions, issues) are explicitly welcome!

Please get involved by extending the project or interacting with us by submitting an issue, contact us (e.g. [here](https://www.embl.de/research/units/scb/bork/members/index.php?s_personId=CP-60028623)). Particular extensions wanted are: Simplify the pyprl library fork to the needed tools in this context; further development of the GUI for the user/experimentor and to change the sorting parameters; collecting custom droplet sorting challenges not currently well addressed by exsisting literature examples; extension to more-dimensional questions (boards with more fast analougue inputs-outputs, sorting based on spectral analysis with detector array, sorting based on 2D detector arrays such as imaging detectors, sorting with additional sensor to verify positive sorting events, etc.).
