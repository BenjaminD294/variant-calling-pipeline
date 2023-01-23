# Variant Calling Pipeline for Spike Protein

This code aims to be a proof-of-concept for a simple variant calling pipeline on different SARSCov-2 Spike gene mutation.

## Installation

In case of you don't want to set up an environement on your machine, a `Dockerfile` containing the whole environment is given. Please reach the next section for more details. I recommend you to use Docker to run this code, as it keeps you from the differences between environments.

If you are on a common UNIX environment (MacOS, common Linux, or Linux subsystem on Windows), you can use `brew` to install the following dependencies:

```sh
brew install pyenv poetry bwa samtools bcftools java
```

In case of you don't have `brew`, your common package manager should give you access to these tools (`apt-get`). In case of Java, please review the after-install instruction from Brew to create a symlink if required, in order to map the Java runtime.

As this application was made with `Python 3.11` in mind, use the following to install Python on your machine:

```sh
pyenv install 3.11
```

As this application uses [Poetry](https://python-poetry.org/) to manage Python dependencies, use the following in the root of this project to create the virtual environment. Poetry is already configured to set it locally, in a `.venv` folder.

```sh
poetry install
```

You may also need some utilies:

```sh
curl -sSL https://github.com/broadinstitute/picard/releases/download/2.27.5/picard.jar -o vendor/picard-2.27.5.jar
```

Note that you might need to change the correct version in `.env` according to the one you've downloaded.

Then, run the application using:

```sh
poetry run python src/main.py
```

Alternatively, a `Makefile` is provided with `make install` and `make run`, leaving plenty of room for improvements.

## Docker environement

[Docker](https://www.docker.com/) allows to you to containerize an application. Use the following command to build and run the image. It should give you results into `out` folder out-of-the-box. **This is the recommended version**, as it provides you a functional environment.

```sh
docker-compose up --build
```

## Resources

- [bcftools](https://samtools.github.io/bcftools/bcftools.html#view)
- [In-depth-NGS-Data-Analysis-Course](https://github.com/hbctraining/In-depth-NGS-Data-Analysis-Course/tree/master/sessionVI/lessons)
- [Running BWA Commands](https://hcc.unl.edu/docs/applications/app_specific/bioinformatics_tools/alignment_tools/bwa/running_bwa_commands/)
- [samtools](http://www.htslib.org/doc/samtools.html)
- [Spike (S) Variants Coding Sequences](https://www.invivogen.com/sars2-spike-vectors)
- [Variant calling](https://samtools.github.io/bcftools/howtos/variant-calling.html)

## Possible future improvements and comments

## Annotations

As I tried to keep the pipeline simple, a further work would be to add annotations. Thus, I need to annotate using `bcftools annotate`, build and use [vt](https://github.com/atks/vt) to decompose then normalize data, and finally annotate using `snpEff` using Spike data from the database. It requires some tuning and additional time to think and compute the pipeline.

## A word on Pipeline design pattern

As I created a Pipeline, I found it suitable to create a Pipeline design pattern. I first used a Builder in the form of a `BuilderCommand`, but I extended it to create a generic `Pipeline` class which encapsulates the application. I could have used libraries like `fastcore` to enhance its functional potential, but I wanted it to keep as low on dependencies as possible. Using this patterns opens a room for keeping intermediate data into memory (thus passing it through the pipeline) in order to avoid having this much of temporary files. The code stays really simple (following KISS and DRY), and lets lots of room for improvement. Finally, I can add unit tests on these utilities in a next version.

### Cloud providers for data processing

The Dockerized version of this project aims to be a sample for computing such project, for bigger genomes, eventually split into servers using orchestrators such as Kubernetes, managed on AWS EBS for instance. Using this kind of mindset is for me essential for bioinformatic: thinking about scalabity in order to use servers or specific architectures (FPGA for instance for high parallelism) is essential for highly demanding work.

### Interactive diagrams with d3

User experience means a lot. Creating pipelines requires in itself a lot of research. I try in my code to create simple, reusable and scalable structure. But visualizing should be also part of the work. Thus, using visualization libraries such as d3 would be interesting. I know that tools like `vcftoolz` would allow to create Venn diagrams but why not creating pimped visuals?
