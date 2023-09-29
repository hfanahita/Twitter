class Database:
    def __init__(self):
        self.tables = []
        self.ids = [0]

    def add_table(self, table):
        if table not in self.tables:
            self.set_id(table)
            self.tables.append(table)

        else:
            return "This table already exists!"

    def remove_table(self, table):
        try:
            self.tables.remove(table)
            self.remove_id(table)
        except:
            return "This table doesn't exist."

    def set_id(self, table):
        table.id = self.ids[-1] + 1
        self.ids.append(self.ids[-1] + 1)
        if self.ids[0] == 0:
            self.ids.remove(0)

    def remove_id(self, table):
        self.ids.remove(table.id)
        table.id = None


class Table:
    def __init__(self, name):
        self.id = 0
        self.name = name
        self.fields = []
        self.set_fields()
        self.fields_properties = {}
        self.set_fields_properties()

    def set_fields_properties(self):
        with open("schema.txt", "r") as schema:
            lines = schema.readlines()
            line_number = lines.index(self.name[:-4] + '\n') + 1
            for line in lines[line_number:]:
                if line != '\n':
                    key = line.split()[0]
                    value = line.split()[1:]
                    self.fields_properties[key] = value
                else:
                    break

    def set_fields(self):
        with open(self.name, "r") as file:
            self.fields = file.readline().split()

    def insert(self, command):
        # $ INSERT INTO <table_name> VALUES (<field1_value>,<field2_value>,<field3_value>);
        field_values = self.translate_insert(command)
        with open(self.name, "a") as f:
            f.write("\n")
            for value in field_values:
                f.write(value)
                f.write(" ")
            f.close()

    def translate_insert(self, command):
        self.check_insert_command(command)
        index = str.index(command, "(")
        command = command[index + 1:-2]
        values = command.split(',')
        return values

    def check_insert_command(self, command):
        # $ INSERT INTO <table_name> VALUES (<field1_value>,<field2_value>,<field3_value>);
        # Checking the general format of the command:
        index = str.index(command, "(")
        if len(command[:index].split()) != 5:
            raise Exception("INSERT command is not correct.")
        # Checking whether the command has its specific words or not:
        standard_command = ["$ INSERT INTO ", " VALUES ", ";"]
        for i in standard_command:
            if i not in command:
                raise Exception("INSERT command is not correct.")
        # Checking the last part of the command [(<field1_value>,<field2_value>,<field3_value>)]:
        last_part = command[index:-1]
        if last_part[0] != "(" or last_part[-1] != ")":
            raise Exception("INSERT command is not correct.")

    def select(self, command):
        # $ SELECT FROM <table_name> WHERE <field_name>==<field_value> OR <field_name>==<field_value>; 
        # Making a set of results to prevent repeated lines in them
        with open(self.name, "r") as file:
            result = set()
            if type(command) == str:
                conditions = self.translate_select(command)
            else:
                conditions = command
            # If there is only one condition, then the program will loop through the table's file and find the matching lines
            if len(conditions) == 1:
                for line in file:
                    field_index = self.fields.index(list(conditions.keys())[0])
                    values = line.split()
                    if values[field_index] == conditions.get(list(conditions.keys())[0]):
                        result.add(line)
                if len(result) != 0:
                    return result
            # If there is only "OR" between conditions,
            # then the program loops through the conditions and then the lines
            # to find matching values from the table's file
            elif conditions[0] == "OR":
                dictionary = {}
                for key in list(conditions[1].keys()):
                    dictionary[self.fields.index(key)] = conditions[1].get(key)
                for field_index in list(dictionary.keys()):
                    for line in file.readlines():
                        values = line.split()
                        if values[field_index] == dictionary[field_index]:
                            result.add(line)
                if len(result) != 0:
                    return result
            # If there is only "AND" between the conditions,
            # Then the program first loops through the lines of the table's file and then in each line loops through the conditions
            # to see if all of them occur, if yes, then it adds the selected line to the result
            elif conditions[0] == "AND":
                dictionary = {}
                for key in list(conditions[1].keys()):
                    dictionary[self.fields.index(key)] = conditions[1].get(key)
                for line in file:
                    found = True
                    values = line.split()
                    for field_index in list(dictionary.keys()):
                        if values[field_index] != dictionary[field_index]:
                            found = False
                            break
                    if found:
                        result.add(line)
                if len(result) != 0:
                    return result
            # If there's a combination of "AND" and "OR" then:
            file.close()
            return "Not Found!"

    def translate_select(self, command):
        self.check_select_syntax(command)
        conditions = command[:-1].split()[5:]
        return self.translate_where(conditions)

    def check_select_syntax(self, command):
        # $ SELECT FROM <table_name> WHERE <field_name>==<field_value> OR <field_name>==<field_value>;
        # Checking that whether the command has its specific words or not:
        standard_command = ["$ SELECT FROM ", " WHERE ", ";"]
        for standard in standard_command:
            if standard not in command:
                raise Exception("SELECT command is not correct.")
        # Checking the last part of the command [<field_name>==<field_value> OR <field_name>==<field_value>]:
        last_part = command.split()[5:]
        # This part also checks whether OR and AND are used correctly or not,
        # because if there's a misspell within these words,
        # then it can't be removed in last_part and it will raise an exception in the if statement
        last_part = list(filter(lambda a: a != "OR", last_part))
        last_part = list(filter(lambda a: a != "AND", last_part))
        for condition in last_part:
            if ("==" not in condition) and ("!=" not in condition):
                raise Exception("SELECT command is not correct.")

    def update(self, command):
        # $ UPDATE <table_name> WHERE <field_name>==<field_value> OR <field_name> == <field_value>
        # VALUES (<field1_value>,<field_value>,<field3_value>);
        translated = self.translate_update(command)
        conditions = translated[0]
        values = translated[1]
        if self.select(conditions) != "Not Found!":
            selected_lines = self.select(conditions)
        lines = []

        with open(self.name, "r") as file:
            for line in file:
                for selected in selected_lines:
                    if line == selected:
                        line = " ".join(values)
                        selected_lines.remove(selected)
                        break
                lines.append(line)
        with open(self.name, "w") as updated:
            updated.writelines(lines)

    def translate_update(self, command):

        self.check_update_syntax(command)
        # Conditions are in this form: ["<field_name>==<field_value>", "OR", "<field_name> == <field_value>"]
        index = str.index(command, "(")
        conditions = (((command[:index]).split(" "))[:-2])[4:]
        translated_conditions = self.translate_where(conditions)
        values = (command[index + 1:-2]).split(",")
        return [translated_conditions, values]

    def check_update_syntax(self, command):
        # $ UPDATE <table_name> WHERE <field_name>==<field_value> OR <field_name>==<field_value>
        # VALUES (<field1_value>,<field_value>,<field3_value>);
        # Checking whether the command has its specific words or not:
        standard_command = ["$ UPDATE ", " WHERE ", "VALUES", ";"]
        for standard in standard_command:
            if standard not in command:
                raise Exception("UPDATE command is not correct.")
        index = str.index(command, "(")
        # part1 format: ['usernam==anahita', 'OR', 'password==sdkfjsdhgis']
        part1 = ((command[:index]).split(" "))[:-2]
        part2 = command[index:-1]
        # part2 = command.split()[-1][:-1]
        part1 = part1[4:]
        # This part also checks whether OR and AND are used correctly or not,
        # because if there's a misspell within these words,
        # then it can't be removed in part1 and it will raise an exception in the if statement
        part1 = list(filter(lambda a: a != "OR", part1))
        part1 = list(filter(lambda a: a != "AND", part1))
        for condition in part1:
            if ("==" not in condition) and ("!=" not in condition):
                raise Exception("UPDATE command is not correct.")
        # part2
        number_of_fields = len(self.fields)
        number_of_values = len(part2.split(','))
        if number_of_fields != number_of_values:
            raise Exception("UPDATE command is not correct.")

    def delete(self, command):
        # $ DELETE FROM <table_name> WHERE <field_name>==<field_value> OR <field_name>==<field_value>;
        translated_conditions = self.translate_delete(command)
        selected_lines = []
        if self.select(translated_conditions) != "Not Found!":
            selected_lines = self.select(translated_conditions)
        lines = []
        with open(self.name, 'r') as file:
            for line in file.readlines():
                found = False
                for selected in selected_lines:
                    if selected == line:
                        found = True
                        lines.append('\n')
                if not found:
                    lines.append(line)
        with open(self.name, 'w') as file:
            file.writelines(lines)

    def translate_delete(self, command):
        # $ DELETE FROM <table_name> WHERE <field_name>==<field_value> OR <field_name>==<field_value>;
        self.check_delete_syntax(command)
        conditions = command[:-1].split()[5:]
        return self.translate_where(conditions)

    def check_delete_syntax(self, command):
        # $ DELETE FROM <table_name> WHERE <field_name>==<field_value> OR <field_name>==<field_value>;
        # Checking whether the command has its specific words or not:
        standard_command = ["$ DELETE FROM ", " WHERE ", ";"]
        for standard in standard_command:
            if standard not in command:
                raise Exception("DELETE command is not correct.")
        # Checking the last part of the command [<field_name>==<field_value> OR <field_name>==<field_value>]:
        last_part = command.split()[5:]
        # This part also checks whether OR and AND are used correctly or not,
        # because if there's a misspell within these words,
        # then it can't be removed in last_part and it will raise an exception in the if statement
        last_part = list(filter(lambda a: a != "OR", last_part))
        last_part = list(filter(lambda a: a != "AND", last_part))
        for condition in last_part:
            if ("==" not in condition) and ("!=" not in condition):
                raise Exception("DELETE command is not correct.")

    # def separate_conditions(self, conditions):
    #     level = 0
    #     level_index_tracker = {}
    #     result = []
    #     for i in range(len(conditions)):
    #         if conditions[i] == "(":
    #             level += 1
    #             level_index_tracker[level] = i
    #         elif conditions[i] == ")":
    #             sub_conditions = conditions[level_index_tracker[level] + 1: i]
    #             result.append(sub_conditions)
    #             level_index_tracker.pop(level)
    #             level -= 1
    #     return result

    def translate_where(self, conditions):
        # If there is only one condition then:
        if len(conditions) == 1:
            condition_dictionary = {}
            name_and_value = conditions[0].split("==")
            condition_dictionary[name_and_value[0]] = name_and_value[1]
            return condition_dictionary
        # If there is only "OR" between the conditions then:
        elif "AND" not in conditions and "OR" in conditions:
            # filter(function, iterable)
            # A Lambda Function in Python programming is an anonymous function or a function having no name.
            # It is a small and restricted function having no more than one line.
            # Just like a normal function, a Lambda function can have multiple arguments with one expression.
            conditions = list(filter(lambda a: a != "OR", conditions))
            condition_dictionary = {}
            for condition in conditions:
                name_and_value = condition.split("==")
                condition_dictionary[name_and_value[0]] = name_and_value[1]
            return ["OR", condition_dictionary]
        # If there is only "AND" between the conditions then:
        elif "OR" not in conditions and "AND" in conditions:
            conditions = list(filter(lambda a: a != "AND", conditions))
            condition_dictionary = {}
            for condition in conditions:
                name_and_value = condition.split("==")
                condition_dictionary[name_and_value[0]] = name_and_value[1]
            return ["AND", condition_dictionary]
        # If a combination of "OR" and "AND" is used between the conditions
        # (in this case parentheses must have been used between some of the conditions).
        # Here the program returns some of the sub-conditions that makes the process of checking the conditions easier:
        else:
            return self.separate_conditions(" ".join(conditions))


# Making the database files based on schema.txt
schema = open("schema.txt", "r")
counter = 0
twitter_db = Database()
for line in schema:
    # Making a file for the table with the given name in schema
    if counter == 0:
        name = ""
        for char in line:
            if char == "\n":
                break
            else:
                name += char
        file = open("%s.txt" % name, "w")
        table = Table(file.name)
        counter += 1
        continue
    # If it reaches an empty line, then it closes the table's file
    if line == "\n":
        counter = 0
        file.close()
        table.set_fields()
        twitter_db.add_table(table)
    # Continues reading lines and adds table's fields to its file
    else:
        field_with_its_properties = line.split()
        file.write(field_with_its_properties[0])
        file.write(" ")
        counter += 1
# Reached the last line of schema(adding the last table):
twitter_db.add_table(table)
file.close()
schema.close()
