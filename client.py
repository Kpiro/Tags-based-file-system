import socket
import json

def send_request(command, payload, client_socket):
    try:
        # Crear y enviar la solicitud
        request = {"command": command, "payload": payload}
        client_socket.send(json.dumps(request).encode('utf-8'))

        # Recibir respuesta
        response = client_socket.recv(1024).decode('utf-8')
        print("Response:", json.loads(response))

    except Exception as e:
        print(f"[ERROR] {e}")

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 5000))
    while True:
        print("\n[CLIENT MENU]")
        print("1. Add files with tags")
        print("2. Delete files by tag query")
        print("3. List files by tag query")
        print("4. Add tags to files by tag query")
        print("5. Delete tags from files by tag query")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            files = input("Enter file names (comma-separated): ").split(",")
            files = [file.strip() for file in files]
            tags = input("Enter tags (comma-separated): ").split(",")
            tags = [tag.strip() for tag in tags]
            print(f'Estos son tags: {tags }')
            send_request("add", {"file_list": files, "tag_list": tags},client_socket)

        elif choice == "2":
            query = input("Enter tag query (e.g., 'tag1 in tags AND tag2 in tags'): ")
            send_request("delete", {"tag_query": query},client_socket)

        elif choice == "3":
            query = input("Enter tag query (e.g., 'tag1 in tags OR tag2 in tags'): ")
            send_request("list", {"tag_query": query},client_socket)

        elif choice == "4":
            query = input("Enter tag query (e.g., 'tag1 in tags AND tag2 in tags'): ")
            tags = input("Enter tags to add (comma-separated): ").split(",")
            tags = [tag.strip() for tag in tags]
            send_request("add-tags", {"tag_query": query, "tag_list": tags},client_socket)

        elif choice == "5":
            query = input("Enter tag query (e.g., 'tag1 in tags AND tag2 in tags'): ")
            tags = input("Enter tags to delete (comma-separated): ").split(",")
            tags = [tag.strip() for tag in tags]
            send_request("delete-tags", {"tag_query": query, "tag_list": tags},client_socket)

        elif choice == "6":
            print("Exiting...")
            client_socket.close()
            break

        else:
            print("Invalid choice. Try again.")
    

if __name__ == "__main__":
    main()
