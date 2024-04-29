#Still a work in progress
class Encryption:
    def __init__(self, key):
        self.len_of_key = len(key)
        self.key_binary = self.key_to_binary(key)

    def show_binary(self):
        print(self.file_bin)

    def key_to_binary(self, key):
        l = []
        for i in key:
            l.append(str(bin(ord(i))[2:]))
        return l

    def encryption(self, value):
        self.value = value
        self.file_bin = []
        self.file_bin_e = []
        self.file_bin_new_e = []
        self.file_e1 = ""
        self.file_e = ""
        for f in self.value:
            self.file_bin.append(bin(ord(f))[2:])
        print(value)

        counter = 0
        for i in self.file_bin:
            for k in self.key_binary:
                if counter == 0:
                    i = bin(int(str(i), 2) + int(str(k), 2))
                elif counter == 1:
                    i = bin(int(str(i), 2) + int(str(k), 2))
            self.file_bin_e.append(i[2:])

        count = 0
        for x in self.file_bin_e:
            s = bin(int(str(x), 2) + int(str(self.key_binary[count]), 2))
            if count == self.len_of_key - 1:
                count = 0
            else:
                count += 1
            self.file_bin_new_e.append(s[2:])
        
        print(len(self.file_bin_new_e))
        for e in self.file_bin_new_e:
            self.file_e += str(hex(int(e, 2))).strip("0x")

        print(len(self.file_e))
        return(self.file_e)
    
    def decryption(self, e_value):
        self.file_bin_new_d = []
        self.file_bin_d = []
        self.file_bin_d1 = []
        self.file_d = ""

        print(len(e_value))
        count = 0
        temp = ""
        for i in e_value:
            if count == 2:
                count = 0
                temp += i
                self.file_bin_d1.append(temp)
                temp = ""
            else:
                temp += i
                count += 1

        print(self.file_bin_d1)
        for d in self.file_bin_d1:
            self.file_bin_new_d.append(bin(int(d, base=16))[2:])

        count = 0
        #print(e_value)
        #print(self.file_bin_new_d)
        for x in self.file_bin_new_d:
            s = bin(int(str(x), 2) - int(str(self.key_binary[count]), 2))
            if count == self.len_of_key - 1:
                count = 0
            else:
                count += 1
            self.file_bin_d.append(s[2:])
        
        counter = 0
        for i in self.file_bin_d:
            for k in self.key_binary:
                if counter == 0:
                    i = bin(int(str(i), 2) - int(str(k), 2))
                elif counter == 1:
                    i = bin(int(str(i), 2) - int(str(k), 2))
            self.file_d += str(i[2:])

        value_d = ""
        fileb = ""
        for i in self.file_d:
            if i != "b":
                fileb += i
        self.file_d = fileb
        for i in range(0, len(self.file_d), 7):
            temp_data = int(self.file_d[i:i + 7], 2)
            value_d += chr(temp_data)
        
        return(value_d)

