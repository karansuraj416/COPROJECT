import sys


opcode = {
    'add': '0110011',
    'sub': '0110011',
    'sll':'0110011',
    'slt':'0110011',
    'sltu':'0110011',
    'xor':'0110011',
    'srl':'0110011',
    'or':'0110011',
    'and':'0110011',
    'lw':'0000011',
    'addi':'0010011',
    'sltui':'0010011',
    'jalr':'1100111',
    'sw':'0100011',
    'beq':'1100011',
    'bne':'1100011',
    'blt':'1100011',
    'bge':'1100011',
    'bltu':'1100011',
    'bgeu':'1100011',
    'lui':'0110111',
    'auipc':'0010111',
    'jal':'1101111'
}


func3 = {
    'add': '000',
    'sub': '000',
    'sll':'001',
    'slt':'010',
    'sltu':'011',
    'xor':'100',
    'srl':'101',
    'or':'110',
    'and':'111',
    'lw':'010',
    'addi':'000',
    'sltui':'011',
    'jalr':'000',
    'sw':'010',
    'beq':'000',
    'bne':'001',
    'blt':'100',
    'bge':'101',
    'bltu':'110',
    'bgeu':'111'

}


registers_in_bin = {
    'zero': '00000', 'ra': '00001', 'sp': '00010', 'gp': '00011',
    'tp': '00100', 't0': '00101', 't1': '00110', 't2': '00111',
    's0': '01000', 's1': '01001', 'a0': '01010', 'a1': '01011',
    'a2': '01100', 'a3': '01101', 'a4': '01110', 'a5': '01111',
    'a6': '10000', 'a7': '10001', 's2': '10010', 's3': '10011',
    's4': '10100', 's5': '10101', 's6': '10110', 's7': '10111',
    's8': '11000', 's9': '11001', 's10': '11010', 's11': '11011',
    't3': '11100', 't4': '11101', 't5': '11110', 't6': '11111',
}

def labels(assembly_code):
    
    labels = {}
    line_number = 0
    for line in assembly_code:
        line = line.strip()
        if ":" in line:
            label, *instruction = line.split(":")
            labels[label.strip()] = line_number
            if instruction:
                line_number += 1  
        elif line:
            line_number += 1
    return labels

def instruction_conversion(instruction, labels, pointer):
   
    parts = instruction.split()
    if not parts:
        return None  
    
    opcode_value = opcode.get(parts[0])
    if not opcode_value:
        return f"Error: Unknown instruction at line {pointer}"

   
    if parts[0] in ['add', 'sub', 'and', 'or', 'slt', 'sltu','sll','xor','srl']:
        funct7 = '0100000' if parts[0] == 'sub' else '0000000'
        return funct7 + registers_in_bin.get(parts[3]) + registers_in_bin.get(parts[2]) + func3.get(parts[0]) + registers_in_bin.get(parts[1]) + opcode_value

    elif parts[0] in ['lw', 'addi','sltiu','jalr']:
        destination = registers_in_bin.get(parts[1])
        
        if "(" in parts[2]: 
            offset, reg = parts[2].replace("(", " ").replace(")", "").split()
            rs1 = registers_in_bin.get(reg)
        else:
            rs1 = registers_in_bin.get(parts[2])
            offset = parts[3] if len(parts) > 3 else '0'

        imm = int(offset) if offset.lstrip('-').isdigit() else labels.get(offset, 0) - pointer
        imm_binary = format(imm & 0xFFF, '012b')
        return imm_binary + rs1 + func3.get(parts[0]) + destination + opcode_value

    elif parts[0] == 'sw':
        offset, reg = parts[2].replace("(", " ").replace(")", "").split()
        rs1 = registers_in_bin.get(reg)
        rs2 = registers_in_bin.get(parts[1])
        imm = int(offset) if offset.lstrip('-').isdigit() else labels.get(offset, 0) - pointer
        imm_binary = format(imm & 0xFFF, '012b')
        return imm_binary[:7] + rs2 + rs1 + func3.get(parts[0]) + imm_binary[7:] + opcode_value

    elif parts[0] in ['beq','bne','blt','bge','bltu','bgeu']:
        rs1 = registers_in_bin.get(parts[1])
        print(rs1)
        rs2 = registers_in_bin.get(parts[2])
        print(rs2)

        if pointer == len(assembly_code)-1:
            offset = 0
        else:
            offset = (labels.get(parts[3], 0) - pointer) * 4
        print(offset)
        imm_binary = format(offset & 0x1FFF, '013b')
        print(imm_binary)

        imm_12 = imm_binary[0]
        imm_10_5 = imm_binary[1:7]
        imm_4_1 = imm_binary[7:11]
        imm_11 = imm_binary[11]
        return imm_12 + imm_10_5 + rs2 + rs1 + func3.get(parts[0]) +  imm_4_1 + imm_11  + opcode_value

    elif parts[0] == 'jal':
        destination = registers_in_bin.get(parts[1])
        offset = (labels.get(parts[2], 0) - pointer) * 4
        imm_binary = format(offset & 0x1FFFFF, '021b')
        return imm_binary[0] + imm_binary[10:20] + imm_binary[9] + imm_binary[1:9] + destination + opcode.get(parts[0])
    
    return f"Error: Invalid instruction format at line {pointer}"

pm1 = sys.argv[1]
pm2 = sys.argv[2]

with open(pm1, 'r') as file:
    assembly_code = file.read().splitlines()

labels = labels(assembly_code)

binary_code = []
pointer = 0

for line in assembly_code:
    line = line.strip()
    if ":" in line:  
        label, *instruction = line.split(":")
        if instruction:
            line = instruction[0].strip()
        else:
            continue
    
    x = line.split(',')
    x1 = x[0].split()
    if len(x) == 2:
        subset_collection = x1[0].strip() + ' ' + x1[1].strip() + ' ' + x[1].strip()
    elif len(x) == 3:
        subset_collection = x1[0].strip() + ' ' + x1[1].strip() + ' ' + x[1].strip() + ' ' + x[2].strip()
    else:
        subset_collection = "Error"

    binary_code.append(instruction_conversion(subset_collection, labels, pointer))
    pointer += 1

with open(pm2, 'w') as file:
    for binary_instruction in binary_code:
        file.write(binary_instruction + '\n')



