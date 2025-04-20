from Bio import Entrez, SeqIO

# Always provide an email when using Entrez
Entrez.email = "chwordal@gmail.com"  

# The accession number identifies the DNA sequence you want to retrieve.
# NC_000913.3 corresponds to the complete genome of Escherichia coli K-12 substr. MG1655.
accession_number = "NC_000913.3"

# Fetch the record from the NCBI database
# 'efetch' retrieves data in the specified format (FASTA in this case)
with Entrez.efetch(db="nucleotide", id=accession_number, rettype="fasta", retmode="text") as handle:
    # Parse the record using SeqIO
    record = SeqIO.read(handle, "fasta")
    dna_sequence = record.seq
# Output key details about the sequence
print(f"Sequence ID: {record.id}")  # Display the sequence ID
print(f"Sequence Length: {len(record.seq)}")  # Display the total length of the sequence
print(dna_sequence[:100])  # Display the first 100 bases of the sequence