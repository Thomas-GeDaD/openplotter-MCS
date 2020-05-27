## openplotter-MCS

This is a App for Openplotter 2.0 and higher to use with a GeDaD MarineControlServer Hardware

### Installing

#### For production

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production** and just install this app from *OpenPlotter Apps* tab.

#### For development

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **development**.

Clone the repository:

`git clone https://github.com/Thomas-GeDaD/openplotter-MCS`

Make your changes and create the package:

```
cd openplotter-MCS
dpkg-buildpackage -b
```

Install the package:

```
cd ..
sudo dpkg -i openplotter-mcs_x.x.x-xxx_all.deb
```

Run post-installation script:

`sudo MCSPostInstall`

Run:

`openplotter-MCS`


Make your changes and repeat package, installation and post-installation steps to test. Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://cloudsmith.io/~thomas-gersmann/repos/openplotter-mcs/packages/detail/deb/openplotter-mcs/2.1.2-dev/d=debian%252Fbuster;t=1/).

### Documentation

[GeDaD Support Site](https://www.gedad.de/support/)
[Openplotter Support Forum](http://forum.openmarine.net/showthread.php?tid=1807)


### Support

t.gersmann@gmail.com


### Where to buy

https://www.gedad.de/shop/gecos-wired/#cc-m-product-15562399022


