import sys
import os

def sign_extend(value, bits):
    """Sign extend a value with given number of bits"""
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)


def initialize_simulator():
    """Initialize simulator state"""
    # Registers x0-x31 (x0 is hardwired to 0)
    registers = [0] * 32
    
    # Program counter
    pc = 0
    
    # Data memory (32 locations)
    memory = [0] * 32
    
    # Instruction type decoding
    opcodes = {
        0b0110011: 'R',
        0b0010011: 'I',
        0b0000011: 'I',  # LOAD
        0b1100111: 'I',  # JALR
        0b0100011: 'S',
        0b1100011: 'B',
        0b0110111: 'U',  # LUI
        0b0010111: 'U',  # AUIPC
        0b1101111: 'J'   # JAL
    }
    
    # funct3 mappings for different instruction types
    funct3_map = {
        'R': {
            0b000: 'add' if 0b0000000 else 'sub',
            0b010: 'slt',
            0b101: 'srl',
            0b110: 'or',
            0b111: 'and'
        },
        'I': {
            0b000: 'addi',
            0b010: 'lw',
            0b000: 'jalr'
        },
        'S': {0b010: 'sw'},
        'B': {
            0b000: 'beq',
            0b001: 'bne',
            0b100: 'blt'
        },
        'J': {0b000: 'jal'}
    }
    
    return registers, pc, memory, opcodes, funct3_map

def parse_instruction(instruction, opcodes, funct3_map):
    """Parse a 32-bit RISC-V instruction"""
    opcode = instruction & 0x7f
    instr_type = opcodes.get(opcode, None)
    
    if not instr_type:
        raise ValueError(f"Unknown opcode: {opcode:07b}")
    
    rd = (instruction >> 7) & 0x1f
    funct3 = (instruction >> 12) & 0x7
    rs1 = (instruction >> 15) & 0x1f
    rs2 = (instruction >> 20) & 0x1f
    funct7 = (instruction >> 25) & 0x7f
    
    # Get instruction name
    instr_name = funct3_map[instr_type].get(funct3, None)
    if not instr_name:
        raise ValueError(f"Unknown funct3: {funct3:03b} for type {instr_type}")
    
    # Handle different instruction types
    if instr_type == 'R':
        return {
            'type': 'R',
            'name': instr_name,
            'rd': rd,
            'rs1': rs1,
            'rs2': rs2,
            'funct7': funct7
        }
    elif instr_type in ['I', 'S', 'B', 'J']:
        # Immediate handling for different instruction types
        if instr_type == 'I':
            imm = (instruction >> 20) & 0xfff
            imm = sign_extend(imm, 12)
        elif instr_type == 'S':
            imm = ((instruction >> 25) & 0x7f) << 5
            imm |= ((instruction >> 7) & 0x1f)
            imm = sign_extend(imm, 12)
        elif instr_type == 'B':
            imm = ((instruction >> 31) & 0x1) << 12
            imm |= ((instruction >> 25) & 0x3f) << 5
            imm |= ((instruction >> 8) & 0xf) << 1
            imm |= ((instruction >> 7) & 0x1) << 11
            imm = sign_extend(imm, 13)
        elif instr_type == 'J':
            imm = ((instruction >> 31) & 0x1) << 20
            imm |= ((instruction >> 21) & 0x3ff) << 1
            imm |= ((instruction >> 20) & 0x1) << 11
            imm |= ((instruction >> 12) & 0xff) << 12
            imm = sign_extend(imm, 21)
        
        return {
            'type': instr_type,
            'name': instr_name,
            'rd': rd,
            'rs1': rs1,
            'rs2': rs2 if instr_type in ['S', 'B'] else None,
            'imm': imm
        }

def execute_instruction(instr, registers, pc, memory):
    """Execute a parsed instruction and return updated pc"""
    if instr['name'] == 'add':
        registers[instr['rd']] = registers[instr['rs1']] + registers[instr['rs2']]
        pc += 4
    elif instr['name'] == 'sub':
        registers[instr['rd']] = registers[instr['rs1']] - registers[instr['rs2']]
        pc += 4
    elif instr['name'] == 'slt':
        registers[instr['rd']] = 1 if registers[instr['rs1']] < registers[instr['rs2']] else 0
        pc += 4
    elif instr['name'] == 'srl':
        registers[instr['rd']] = registers[instr['rs1']] >> (registers[instr['rs2']] & 0x1f)
        pc += 4
    elif instr['name'] == 'or':
        registers[instr['rd']] = registers[instr['rs1']] | registers[instr['rs2']]
        pc += 4
    elif instr['name'] == 'and':
        registers[instr['rd']] = registers[instr['rs1']] & registers[instr['rs2']]
        pc += 4
    elif instr['name'] == 'addi':
        registers[instr['rd']] = registers[instr['rs1']] + instr['imm']
        pc += 4
    elif instr['name'] == 'lw':
        addr = registers[instr['rs1']] + instr['imm']
        if 0 <= addr // 4 < len(memory):
            registers[instr['rd']] = memory[addr // 4]
        else:
            raise ValueError(f"Memory access out of bounds: {addr}")
        pc += 4
    elif instr['name'] == 'sw':
        addr = registers[instr['rs1']] + instr['imm']
        if 0 <= addr // 4 < len(memory):
            memory[addr // 4] = registers[instr['rs2']]
        else:
            raise ValueError(f"Memory access out of bounds: {addr}")
        pc += 4
    elif instr['name'] == 'beq':
        if registers[instr['rs1']] == registers[instr['rs2']]:
            pc += instr['imm']
        else:
            pc += 4
    elif instr['name'] == 'bne':
        if registers[instr['rs1']] != registers[instr['rs2']]:
            pc += instr['imm']
        else:
            pc += 4
    elif instr['name'] == 'blt':
        if registers[instr['rs1']] < registers[instr['rs2']]:
            pc += instr['imm']
        else:
            pc += 4
    elif instr['name'] == 'jal':
        registers[instr['rd']] = pc + 4
        pc += instr['imm']
    elif instr['name'] == 'jalr':
        registers[instr['rd']] = pc + 4
        pc = (registers[instr['rs1']] + instr['imm']) & ~1  # Clear LSB
    else:
        raise ValueError(f"Unknown instruction: {instr['name']}")
    
    return pc

def run_simulation(binary_file, output_file):
    """Run simulation from binary file and write output"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    registers, pc, memory, opcodes, funct3_map = initialize_simulator()
    
    with open(binary_file, 'r') as f:
        instructions = [line.strip() for line in f if line.strip()]
    
    with open(output_file, 'w') as f_out:
        while pc // 4 < len(instructions):
            # Get current instruction
            try:
                instruction = int(instructions[pc // 4], 2)
            except:
                raise ValueError(f"Invalid binary instruction at PC {pc}: {instructions[pc // 4]}")
            
            # Parse and execute
            parsed_instr = parse_instruction(instruction, opcodes, funct3_map)
            pc = execute_instruction(parsed_instr, registers, pc, memory)
            
            # Virtual halt instruction (beq zero,zero,0)
            if (parsed_instr['name'] == 'beq' and 
                parsed_instr['rs1'] == 0 and 
                parsed_instr['rs2'] == 0 and 
                parsed_instr['imm'] == 0):
                break
            
            # Write register state to output
            f_out.write(f"{pc:032b} ")
            f_out.write(" ".join(f"{reg:032b}" for reg in registers))
            f_out.write("\n")
        
        # After halt, write memory contents
        for i in range(len(memory)):
            f_out.write(f"{memory[i]:032b}\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: python simulator.py <input_binary_file> <output_trace_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    run_simulation(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()