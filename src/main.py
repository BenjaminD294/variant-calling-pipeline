import os
import shutil

from dotenv import load_dotenv
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from Pipeline.Command import RunCommand, WriteFileCommand
from Pipeline.Pipeline import Pipeline


def main() -> None:
    """
    Implements a variant calling pipeline for SARSCov-2 Spike gene mutations
    It takes a reference sequence from the original Wuhan strain of the Spike gene, then compares it with the Spike protein gene in a few SARSCov-2 variants.
    """
    load_dotenv()

    cleanup_environment()
    convert_sequences_to_fasta()
    run_pipeline()


def cleanup_environment() -> None:
    """Creates temporary folders then cleans up out directory."""
    try:
        shutil.rmtree(os.getenv("TEMP_FOLDER"))
    except FileNotFoundError:
        pass

    try:
        with os.scandir("./out") as entry_iterator:
            for entry in entry_iterator:
                if entry.name.startswith("."):
                    continue
                if entry.is_file():
                    os.unlink(entry.path)
                if entry.is_dir():
                    shutil.rmtree(entry.path)
    except FileNotFoundError:
        pass

    os.makedirs(os.getenv("FASTA_FOLDER"))
    os.makedirs(os.getenv("TEMP_FOLDER"))


def convert_sequences_to_fasta() -> None:
    """Converts a nucleotide sequence from a text file into FASTA format."""

    with os.scandir("data/genes") as spike_sequence_iterator:
        for spike_sequence in spike_sequence_iterator:
            spike_sequence_name = spike_sequence.name.split(".")[0]

            with open(spike_sequence.path, "r") as f:
                fasta_sequence = SeqRecord(
                    Seq(f.read().rstrip()),
                    id=spike_sequence_name.replace("-", "_"),
                    name=spike_sequence_name,
                    description="",
                )

                with open(
                    "{}/{}.fasta".format(os.getenv("FASTA_FOLDER"), spike_sequence_name),
                    "w",
                ) as fasta:
                    fasta.write(fasta_sequence.format("fasta"))


def run_pipeline() -> None:
    """Executes the variant calling pipeline for each sequence."""
    ref_genome = "{}/{}.fasta".format(os.getenv("FASTA_FOLDER"), os.getenv("REFERENCE_GENOME"))

    with os.scandir(os.getenv("FASTA_FOLDER")) as fasta_file_iterator:
        for fasta_file in fasta_file_iterator:
            alt_genome = fasta_file.path

            if alt_genome == ref_genome:
                continue

            index_prefix = "{}/{}".format(os.getenv("TEMP_FOLDER"), fasta_file.name.split(".")[0])
            out_alt_genome = "{}/{}".format(os.getenv("OUT_FOLDER"), fasta_file.name.split(".")[0])

            align_reads(ref_genome, alt_genome, index_prefix)
            compute_variant_calling(ref_genome, index_prefix, out_alt_genome)


def align_reads(ref_genome: str, alt_genome: str, index_prefix: str) -> None:
    """
    Computes the alignement between two sequences and stores both SAM and BAM values.
    Compares every sequence with a reference genome.
    """
    (
        Pipeline()
        .add(RunCommand("bwa index -a is -p {} {}".format(index_prefix, ref_genome)))
        .add(RunCommand("bwa mem -A2 -E1 -B1 {} {}".format(index_prefix, alt_genome)))
        .add(WriteFileCommand("{}.sam".format(index_prefix)))
        .add(
            RunCommand(
                "java -Xmx1G -jar vendor/picard-{picard}.jar SortSam\
                    INPUT={idx}.sam \
                    OUTPUT={idx}_sorted.sam \
                    SORT_ORDER=coordinate".format(
                    picard=os.getenv("VENDOR_PICARD_VERSION"), idx=index_prefix
                )
            )
        )
        .add(
            RunCommand(
                "java -Xmx1G -jar vendor/picard-{picard}.jar MarkDuplicates\
                    INPUT={idx}_sorted.sam \
                    OUTPUT={idx}_sorted_marked.bam \
                    METRICS_FILE={idx}_metrics.txt \
                    ASSUME_SORTED=true".format(
                    picard=os.getenv("VENDOR_PICARD_VERSION"), idx=index_prefix
                )
            )
        )
        .add(RunCommand("samtools index {}_sorted_marked.bam".format(index_prefix)))
        .pipe()
    )


def compute_variant_calling(ref_genome: str, index_prefix: str, out_alt_genome: str) -> None:
    """Executes variant calling using two utilities to compare results."""
    (
        Pipeline()
        # Variant calling using freebayes
        .add(
            RunCommand(
                "freebayes -f {} --use-duplicate-reads -C 1 {}_sorted_marked.bam".format(ref_genome, index_prefix)
            )
        )
        .add(WriteFileCommand("{}-freebayes.vcf".format(out_alt_genome)))
        # Variant calling using bcftools
        .add(RunCommand("bcftools mpileup -f {} {}_sorted_marked.bam".format(ref_genome, index_prefix)))
        .add(RunCommand("bcftools call -mv -Ov -o {}-bcftools.vcf".format(out_alt_genome), pipe_stdin=True))
        .pipe()
    )


if __name__ == "__main__":
    main()
