# FlatFinder

This tool can help you find your perfect apartment for rent when 
it is crucial to contact landlord within minutes after the ad was published.


## Installation

> FlatFinder requires a MongoDB instance running somewhere.

Install from source:
```bash
git clone https://github.com/haberrr/flatfinder.git
cd flatfinder
pip install .
```

<details>
<summary>Using with MongoDB Docker image</summary>

The simplest way to use FlatFinder is to employ MongoDB Docker image.

1. Install Docker
2. Pull MongoDB image:
    ```bash
    docker pull mongo:latest
    ```
3. Run container:
    ```bash
    docker run --name <some-container-name> -d -p 27017:27017
    ```
4. FlatFinder should be able to connect to MongoDB with default configuration in `config.yaml`
</details>


## Configuration

There is a template `config.yaml` file that should be filled in order to run FlatFinder from the CLI. 
Once filled it can either be places to a `~/.config/flatfinder/config.yaml` or its location can be specified 
by setting the environment variable `FLATFINDER_CONFIG`.


## Examples

You can set up crontab with the required polling frequency for each source website, for example:
```
15 * * * * flatfinder -n cityexpert
15 * * * * flatfinder -n halooglasi
15 * * * * flatfinder -n nekretnine
```

> Do not forget to add virtualenv with installed FlatFinder to the PATH at the top of crontab 