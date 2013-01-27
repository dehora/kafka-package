## Kafka Debian File ##

Creates a kafka .deb file via [fpm](https://github.com/jordansissel/fpm/wiki).

### Usage

    ./build.py [OPTIONS]

    Options:

     REQUIRED [-r, --release] <kafka version>  create a deb named as this version

     REQUIRED [-l, --link] <kafka url> download/unpack source release (assumes a tgz)

     REQUIRED [-m, --maintainer] <package> package maintainer

     REQUIRED [-v, --vendor] <vendor> package vendor

     OPTIONAL [-p, --package-release] <package version>  package release version (default is 1)

     OPTIONAL [-s, --source-folder] <folder name>  name of unpacked source (default takes from downloaded file)

### Example

    ./build.py -r 0.7.2-incubating -l http://www.eu.apache.org/dist/incubator/kafka/kafka-0.7.2-incubating/kafka-0.7.2-incubating-src.tgz -m bobfisch@example.org -v Example

