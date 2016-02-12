#OSM Tiles Download

Creates a full size jpg map from tiles available from openstreet map. 

The openstreetmap tiles are downloaded using all different tile servers available(known). This is done asynchronously to make the download of tiles as fast as possible. The different tiles are then merged into a full sized map in jpg format to be use in your GPS or computer.

The following map tile styles are allowed : **sat landscape outdoors transport cycle**

# Generic Use
The ```osm_download.py``` script creates a full size jpg map only and outputs the map path. No other fancy thing.

### Examples:
```bash
./osm_download.py $map_name $latitude_center $longitude_center $zoom_level $distance_in_kms_from_lat_lon_center $map_tile_style $output_dir;
./osm_download.py hobart -42.85 147.194824219 14 10 cycle `mktemp -d` | xargs display;
./osm_download.py hobart -42.85 147.194824219 11 30 sat `mktemp -d`;
```


# Use with OGIE3D flight data analyser for paragliding

The ```osm_ogie3d.py``` python script is to be used in conjonction with **OGIE3D** and *GPLIGC** softwares for paragliding. http://pc12-c714.uibk.ac.at/GPLIGC/GPLIGC.html

This script reads the LAT LON boundaries (an offset of 0.027 degrees is added) from an IGC file and downloads tiles from openstreetmap. 

The file is moved to the ```$HOME/.gpligc/map``` folder if exists and the various information
needed (map file path, corner coordinates) are added to the ```$HOME/.ogierc``` config file for OGIE3D software.

### Examples:
 ```bash
 ./osm_ogie3d.py $igc_file ;
 ./osm_ogie3d.py $igc_file $map_name $zoom_level $map_tile_style; # optional arguments
 ./osm_ogie3d.py example/2016-02-02-FLY-5348-01.IGC mount_wellington 15 outdoors | xargs display;
 ./osm_ogie3d.py igcFile.igc testmap 11 sat;
```

### bash complete
This is a complete example to put in your ```~/.complete``` or ```~/.bashrs```
```bash
IGC_DIR='PLEASE ADD PATH TO IGC FILES'
_list_igc_files() {
    local curr_arg
    local option_list

    curr_arg=${COMP_WORDS[COMP_CWORD]};
    option_list=`ls $IGC_DIR/*.IGC`
    COMPREPLY=( $(compgen -W '`echo $option_list`' -- $curr_arg ) );
}

alias paragliding_create_osm_map='PATH TO OSM_Tile_Download/osm_ogie3d.py'
complete -F _list_igc_files paragliding_create_osm_map
```

### OGIE3D, GPLIGC paragliding software - install tips
Read documention found in http://pc12-c714.uibk.ac.at/GPLIGC/GPLIGC.html in order to use OGIE3D

This software needs to be compiled from the sources, but a compiled version (by myself) is available at https://github.com/lbesnard/chef_laptop/blob/master/dpkg/gpligc_1.10pre7-1_amd64.deb

Make sure to install the different debian packages:
apt-get install freeglut3 freeglut3-dev gnuplot perl-tk xterm gnuplot-x11



# Requirements
pip install grequests
python-geopy
imagemagick

... Linux . Have no idea if this would work on OSX

