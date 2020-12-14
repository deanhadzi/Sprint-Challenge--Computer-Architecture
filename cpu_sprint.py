"""CPU functionality."""

import sys

ADD = 0b10100000  # ALU
AND = 0b10101000  # ALU
CALL = 0b01010000
CMP = 0b10100111  # ALU
HLT = 0b00000001
JEQ = 0b01010101
JMP = 0b01010100
JNE = 0b01010110
LDI = 0b10000010
MOD = 0b10100100  # ALU
MUL = 0b10100010  # ALU
NOT = 0b01101001  # ALU
OR = 0b10101010  # ALU
POP = 0b01000110
PRN = 0b01000111
PUSH = 0b01000101
RET = 0b00010001
SHL = 0b10101100  # ALU
SHR = 0b10101101  # ALU
XOR = 0b10101011  # ALU
SP = 7  # initial stack pointer


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0  # program counter
        self.ir = 0  # instruction register
        self.fl = 0b00000000  # flag register
        self.ram = [0] * 256
        self.halted = False

        self.branchtable = {
            CALL: self.call,
            HLT: self.hlt,
            JEQ: self.jeq,
            JMP: self.jmp,
            JNE: self.jne,
            LDI: self.ldi,
            POP: self.pop,
            PRN: self.prn,
            PUSH: self.push,
            RET: self.ret,
        }

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        try:
            with open(filename) as f:
                for line in f:
                    comment_split = line.split("#")
                    bin_num = comment_split[0]
                    try:
                        x = int(bin_num.strip(), 2)
                        self.ram_write(address, x)
                        address += 1
                    except:
                        continue
        except FileNotFoundError:
            print('File not found.')

    def alu(self, instruction, reg_a, reg_b):
        """ALU operations."""

        # Add the value in two registers and store the result in registerA.
        if instruction == ADD:
            self.reg[reg_a] += self.reg[reg_b]

        # Bitwise-AND the values in registerA and registerB,
        # then store the result in registerA.
        elif instruction == AND:
            self.reg[reg_a] &= self.reg[reg_b]

        # Compare the values in two registers.
        elif instruction == CMP:
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000001

        # Divide the value in the first register by the value in the second,
        # storing the remainder of the result in registerA.
        # If the value in the second register is 0,
        # the system should print an error message and halt.
        elif instruction == MOD:
            if self.reg[reg_b] == 0:
                self.hlt(reg_a, reg_b)
            else:
                self.reg[reg_a] = self.reg[reg_a] % self.reg[reg_b]

        # Multiply the values in two registers together
        # and store the result in registerA.
        elif instruction == MUL:
            self.reg[reg_a] *= self.reg[reg_b]

        # Perform a bitwise-NOT on the value in a register,
        # storing the result in the register.
        elif instruction == NOT:
            self.reg[reg_a] = ~self.reg[reg_a]

        # Perform a bitwise-OR between the values in registerA and registerB,
        # storing the result in registerA.
        elif instruction == OR:
            self.reg[reg_a] |= self.reg[reg_b]

        # Shift the value in registerA left by the number of bits specified in registerB,
        # filling the low bits with 0.
        elif instruction == SHL:
            self.reg[reg_a] <<= self.reg[reg_b]

        # Shift the value in registerA right by the number of bits specified in registerB,
        # filling the high bits with 0.
        elif instruction == SHR:
            self.reg[reg_a] >>= self.reg[reg_b]

        # Perform a bitwise-XOR between the values in registerA and registerB,
        # storing the result in registerA.
        elif instruction == XOR:
            self.reg[reg_a] ^= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, address):
        """Return the RAM value at given address."""
        return self.ram[address]

    def ram_write(self, address, value):
        """Write the value at given RAM address"""
        self.ram[address] = value

    def run(self):
        """Run the CPU."""

        while not self.halted:

            # Set the instruction register.
            self.ir = self.ram_read(self.pc)

            # Decode the instruction.
            num_args = self.ir >> 6
            is_alu_op = (self.ir >> 5) & 0b001
            pc_setter = (self.ir >> 4) & 0b0001

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if is_alu_op == 1:
                self.alu(self.ir, operand_a, operand_b)

            else:
                self.branchtable[self.ir](operand_a, operand_b)

            if pc_setter != 1:
                # increment the pc
                self.pc += num_args + 1

    def call(self, operand_a, operand_b):
        """
        Calls a subroutine (function) at the address stored in the register.
        """
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], self.pc + 2)
        self.pc = self.reg[operand_a]

    def hlt(self, operand_a, operand_b):
        """Halt the CPU (and exit the emulator)."""
        self.halted = True
        sys.exit(-1)

    def jeq(self, operand_a, operand_b):
        """
        If equal flag is set (true), 
        jump to the address stored in the given register.
        """
        if self.fl == 0b00000001:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def jmp(self, operand_a, operand_b):
        """
        Jump to the address stored in the given register.
        Set the PC to the address stored in the given register.
        """
        self.pc = self.reg[operand_a]

    def jne(self, operand_a, operand_b):
        """
        If E flag is clear (false, 0), 
        jump to the address stored in the given register.
        """
        if self.fl != 0b00000001:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def ldi(self, operand_a, operand_b):
        """Set the value of a register to an integer."""
        self.reg[operand_a] = operand_b

    def pop(self, operand_a, operand_b):
        """Pop the value at the top of the stack into the given register."""
        self.reg[operand_a] = self.ram_read(self.reg[SP])
        self.reg[SP] += 1

    def prn(self, operand_a, operand_b):
        """Print numeric value stored in the given register."""
        print(self.reg[operand_a])

    def push(self, operand_a, operand_b):
        """Push the value in the given register on the stack."""
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], self.reg[operand_a])

    def ret(self, operand_a, operand_b):
        """Return from subroutine."""
        self.pc = self.ram_read(self.reg[SP])
