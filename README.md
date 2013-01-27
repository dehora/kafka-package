## Kafka Debian File ##

Creates a kafka .deb file via [fpm](https://github.com/jordansissel/fpm/wiki).

### Usage

    ./build.py [OPTIONS]

    Options:

     REQUIRED [-r, --release] <kafka version>  create a deb named as this version

     REQUIRED [-l, --link] <kafka url> download/unpack source release (assumes a tgz that unpacks to "kafka")

     REQUIRED [-m, --maintainer] <package> package maintainer

     REQUIRED [-v, --vendor] <vendor> package vendor

     OPTIONAL [-p, --package-release] <package version>  package release version (default is 1)

### Example

    ./build.py -r 0.7.2-incubating -l http://www.eu.apache.org/dist/incubator/kafka/kafka-0.7.2-incubating/kafka-0.7.2-incubating-src.tgz -m bobfisch@example.org -v Example

