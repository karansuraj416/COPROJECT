# Importing necessary libraries for file handling and system operations
import sys

# Defining the opcode mappings for different instruction types
op_code_r = {"add": "0110011", "sub": "0110011", "slt": "0110011", "srl": "0110011", "and": "0110011", "or": "0110011"}
op_code_i = {"lw": "0000011", "addi": "0010011", "jalr": "1100111"}
op_code_s = {"sw": "0100011"}
op_code_b = {"beq": "1100011", "bne": "1100011"}
op_code_j = {"jal": "1101111"}

# Initializing registers with their binary representations and default values
registers = {"00000": 0, "00001": 0, "00010": 380, "00011": 0, "00100": 0, "00101": 0, "00110": 0, "00111": 0, "01000": 0, "01001": 0, "01010": 0, "01011": 0, "01100": 0, "01101": 0, "01110": 0, "01111": 0, "10000": 0, "10001": 0, "10010": 0, "10011": 0, "10100": 0, "10101": 0, "10110": 0, "10111": 0, "11000": 0, "11001": 0, "11010": 0, "11011": 0, "11100": 0, "11101": 0, "11110": 0, "11111": 0}

# Function to convert a number to its binary representation
def convert_to_binary(num, bit_length):
    # If he number is negative, convert it to its two's complement representation
    if num < 0:
        num += (1 << bit_length)
    return format(num, f'0{bit_length}b')

# Defining the memory spaces for data
data_mem = {}
for addr in range(0, 128, 4):
    data_mem[f'0x{(0x00010000 + addr):08X}'] = 0

# Defining the memory spaces for stack
stack_mem = {}
for addr in range(0, 128, 4):
    stack_mem[f'0x{(0x00000100 + addr):08X}'] = 0

# Assigning input and output file names from command line arguments
input_file = sys.argv[1]
output_file = sys.argv[2]

# Opening the input file for reading the data inside it by splitting it on the basis of next line
with open(input_file, "r") as f_in:
    lines = f_in.read().split("\n")

# Opening the output file for writing the data inside it
file_oi = open(output_file, "w")

# Opening the trace file for writing the data inside it
trace_file = "trace.txt" if len(sys.argv) < 4 else sys.argv[3]
file_trace = open(trace_file, "w")

# Initializing the program counter and count for iteration
PC = 0
count = 0

# Function to convert binary address to hexadecimal format
def binary_to_hexa(binary_val):
    int_val = int(binary_val, 2)
    return f'0x{int_val:08X}'

# Function to process the immediate value from the instruction
def process_imm(bin_imm):
    if bin_imm[0] == '1':
        inverted = ''.join('1' if bit == '0' else '0' for bit in bin_imm)
        pos_val = int(inverted, 2) + 1
        return -pos_val
    else:
        return int(bin_imm, 2)

# Function to format the register values for output presentation
def form_reg(reg_values):
    form_val = []

    # Iterating through the register values and converting them to binary representation
    for val in reg_values:
        if val < 0:
            val_32bit = (1 << 32) + val
            binary_rep = bin(val_32bit)[2:].zfill(32)
        else:
            binary_rep = bin(val)[2:].zfill(32)
        form_val.append('0b' + binary_rep)
    return form_val

# Reading the instructions from the input file and storing them in instruction memory
instr_mem = {}
for i, line in enumerate(lines):
    if line.strip():
        instr_mem[i*4] = line.strip()

# Loop to execute the instructions
while PC < len(lines) * 4:
    count += 1

    # If the count exceeds 100, break the loop to prevent infinite execution
    if count > 100:
        break

    curr_inst = instr_mem.get(PC, "00000000000000000000000001100011")
    
    # If the instruction is empty, break the loop and write the values to the output file
    if curr_inst == "00000000000000000000000001100011":
        registers["00000"] = 0
        
        reg_values = [PC]
        for reg_key in sorted(registers.keys()):
            reg_values.append(registers[reg_key])
        form_val = form_reg(reg_values)
        file_oi.write(" ".join(form_val) + "\n")
        
        reg_values = [PC]
        for reg_key in sorted(registers.keys()):
            reg_values.append(registers[reg_key])
        file_trace.write(" ".join(str(val) for val in reg_values) + "\n")
        
        break
        
