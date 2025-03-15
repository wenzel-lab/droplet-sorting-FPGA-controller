## Red Pitaya Images

The `rp-images` folder contains different versions of Redpitaya images that have been developed so far. These versions are backed up in case it is necessary to test a previous one, even though it is possible to generate new images using the resources available in the [Pyrpl repository](https://github.com/wenzel-lab/pyrpl/tree/updated-2025).  

The differences between each image lie in certain modifications made to the `red_pitaya_fads.sv` file, which is located in the Pyrpl repository mentioned above.


- `red_pitaya_uncompressed-updated-muxaddr.bit.bin`: The updated version (below) writing the `mux_addr_i` and `muxing_channels_o` variables to the memory space of redpitaya.
- `red_pitaya_uncompressed-updated-signal-duration.bit.bin`: The updated version (below) adding the `signal_duration` variable in `red_pitaya_fads.sv` file.
- `red_pitaya_uncompressed-updated-signed.bit.bin`: The updated version (below) considering as `signed` the voltages variables in `red_pitaya_fads.sv` file.
- `red_pitaya_uncompressed-updated.bit.bin`: Last version created from branch `open_fpga_fads` in [Pyrpl repository](https://github.com/wenzel-lab/pyrpl/tree/open_fpga_fads).  

To use a specific image on the Red Pitaya hardware, it must be placed in the `root/` directory and renamed to `red_pitaya_uncompressed.bit.bin`.
