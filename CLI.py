import DB_Mongo as db_manager


def show(args):
    db_manager.print_all_collections()


def add(args):
    print(f"adding doc to collection {args[0]}")
    print("Define doc:\n")
    doc = dict()
    while key := input("doc key:\n"):
        value = input("Key's value:\n")
        doc[key] = value
    db_manager.add_doc(args[0], doc)


# def parse(command):
#     command, *args = command.split(" ")
#     match command:
#         case "show":
#             db_manager.print_all_collections()
#         case "add":
#             add(args)
#         case _:
#             print(f"{command} not recognised")


COMMANDS = {"show": show,
            "add": add}


def main():
    print("Welcome to Journal CLI")
    print("command list:")
    [print(key) for key in COMMANDS]
    while user_input := input():
        command, *args = user_input.split(" ")
        print(f"{command = }")
        if command in COMMANDS:
            COMMANDS[command](args)
        else:
            print("COMMAND NOT RECOGNISED")





if __name__ == "__main__":
    main()




