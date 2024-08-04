import irc.bot
import irc.connection
import threading
from datetime import datetime, timedelta
import json
import os
import time
import socket

class FileManager:
    @staticmethod
    def load_json(file_path, default_value):
        """Load JSON data from file or return a default value if the file does not exist or is invalid."""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading {file_path}: {e}")
        return default_value

    @staticmethod
    def save_json(file_path, data):
        """Save JSON data to a file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving {file_path}: {e}")

class MessageManager:
    def __init__(self, message_file='messages.json'):
        self.message_file = message_file
        self.messages = FileManager.load_json(self.message_file, {})

    def save_messages(self):
        FileManager.save_json(self.message_file, self.messages)

    def save_message(self, sender, target_nick, message):
        """Save a message for a target user."""
        if target_nick not in self.messages:
            self.messages[target_nick] = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.messages[target_nick].append({
            'sender': sender,
            'timestamp': timestamp,
            'message': message
        })
        print(f"Message saved for {target_nick}: {message}")
        self.save_messages()

class UserManager:
    def __init__(self, user_file='users.json'):
        self.user_file = user_file
        self.users_on_channel = set(FileManager.load_json(self.user_file, []))

    def save_users(self):
        FileManager.save_json(self.user_file, list(self.users_on_channel))

    def add_user(self, nick):
        """Add a user to the channel's user list."""
        self.users_on_channel.add(nick)
        print(f"User added: {nick}")
        self.save_users()

    def remove_user(self, nick):
        """Remove a user from the channel's user list."""
        self.users_on_channel.discard(nick)
        print(f"User removed: {nick}")
        self.save_users()

    def user_exists(self, nick):
        """Check if a user is on the channel."""
        return nick in self.users_on_channel

class AlarmManager:
    def __init__(self, alarm_file='alarms.json'):
        self.alarm_file = alarm_file
        self.alarms = FileManager.load_json(self.alarm_file, [])

    def save_alarms(self):
        FileManager.save_json(self.alarm_file, self.alarms)

    def set_alarm(self, connection, nick, args, channel):
        """Set an alarm for the user."""
        try:
            if len(args) < 2:
                raise ValueError("Incorrect format")
            time_str = args[0]
            message = ' '.join(args[1:])  # Join all elements from the second as a message
            alarm_time = datetime.strptime(time_str, "%H:%M").replace(
                year=datetime.now().year,
                month=datetime.now().month,
                day=datetime.now().day
            )
            if alarm_time < datetime.now():
                alarm_time += timedelta(days=1)
            self.alarms.append((alarm_time.strftime("%Y-%m-%d %H:%M:%S"), nick, message))
            self.save_alarms()
            connection.privmsg(channel, f"{nick}: Alarm ustawiony na {alarm_time.strftime('%H:%M')} z wiadomością: {message}")
        except Exception as e:
            connection.privmsg(channel, f"{nick}: Błąd ustawiania alarmu: {e}")

    def start_alarm_thread(self, connection, channel):
        """Start a thread to check and send alarms."""
        def check_alarms():
            while True:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for alarm in self.alarms[:]:
                    alarm_time, nick, message = alarm
                    if now >= alarm_time:
                        connection.privmsg(channel, f"{nick}: Przypomnienie: {message}")
                        self.alarms.remove(alarm)
                        self.save_alarms()
                time.sleep(30)

        alarm_thread = threading.Thread(target=check_alarms, daemon=True)
        alarm_thread.start()

class TimerManager:
    def __init__(self):
        self.timers = []  # List to store timers

    def set_timer(self, connection, nick, args, channel):
        """Set a timer for the user."""
        try:
            if len(args) < 2:
                raise ValueError("Incorrect format")
            duration_str = args[0]
            message = ' '.join(args[1:])  # Join all elements from the second as a message
            if duration_str.endswith("min"):
                duration = int(duration_str.replace("min", "").strip())
                timer_time = datetime.now() + timedelta(minutes=duration)
            elif duration_str.endswith("h"):
                duration = int(duration_str.replace("h", "").strip())
                timer_time = datetime.now() + timedelta(hours=duration)
            else:
                raise ValueError("Incorrect duration format")
            self.timers.append((timer_time, nick, message))
            connection.privmsg(channel, f"{nick}: Minutnik ustawiony na {duration_str} z wiadomością: {message}")
        except Exception as e:
            connection.privmsg(channel, f"{nick}: Błąd ustawiania minutnika: {e}")

    def start_timer_thread(self, connection, channel):
        """Start a thread to check and send timers."""
        def check_timers():
            while True:
                now = datetime.now()
                for timer_time, nick, message in self.timers[:]:
                    if now >= timer_time:
                        connection.privmsg(channel, f"{nick}: Minutnik: {message}")
                        self.timers.remove((timer_time, nick, message))
                time.sleep(30)

        timer_thread = threading.Thread(target=check_timers, daemon=True)
        timer_thread.start()

class NotkaBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667, bind_address=None,
                 message_file='messages.json', user_file='users.json',
                 alarm_file='alarms.json'):
        self.bind_address = bind_address  # Save the bind address
        # Initialize the connection factory with a custom bind address
        factory = irc.connection.Factory(wrapper=self.create_socket_wrapper())

        super().__init__([(server, port)], nickname, nickname, connect_factory=factory)
        self.channel = channel
        self.reconnect_delay = 10
        self.keep_running = True
        self.last_ping_time = time.time()

        # Initialize managers
        self.message_manager = MessageManager(message_file)
        self.user_manager = UserManager(user_file)
        self.alarm_manager = AlarmManager(alarm_file)
        self.timer_manager = TimerManager()

        # Start threads
        self.start_ping_thread()
        self.alarm_manager.start_alarm_thread(self.connection, self.channel)
        self.timer_manager.start_timer_thread(self.connection, self.channel)

    def create_socket_wrapper(self):
        """Create a function to wrap a socket, binding it to a specified local address."""
        def socket_wrapper(sock):
            sock.bind((self.bind_address, 0))  # Bind to the specified local address
            return sock

        return socket_wrapper

    def on_welcome(self, connection, event):
        """Join the channel after connecting to the server and request user list."""
        connection.join(self.channel)
        connection.names(self.channel)

    def on_namreply(self, connection, event):
        """Populate the user list when joining the channel."""
        for nick in event.arguments[2].split():
            self.user_manager.add_user(nick.strip('@+'))

    def on_endofnames(self, connection, event):
        """Handle end of NAMES list."""
        print("Finished retrieving user list.")

    def on_join(self, connection, event):
        """Add the user to the channel's user list and send saved messages."""
        nick = event.source.nick
        self.user_manager.add_user(nick)
        self.send_saved_messages(connection, nick)

    def on_part(self, connection, event):
        """Remove the user from the channel's user list."""
        nick = event.source.nick
        self.user_manager.remove_user(nick)

    def on_quit(self, connection, event):
        """Remove the user from the channel's user list."""
        nick = event.source.nick
        self.user_manager.remove_user(nick)

    def on_disconnect(self, connection, event):
        """Reconnect if disconnected."""
        while self.keep_running:
            try:
                self.reconnect()
                break
            except Exception as e:
                print(f"Reconnect failed: {e}")
                time.sleep(self.reconnect_delay)

    def on_pubmsg(self, connection, event):
        """Handle public messages and save/retrieve messages."""
        nick = event.source.nick
        message = event.arguments[0].strip()

        # Send saved messages to the user
        self.send_saved_messages(connection, nick)

        # Podziel wiadomość na komendę i argumenty
        if message.startswith("!"):
            parts = message.split(" ", 2)  # Dzielimy na 3 części, aby rozdzielić komendę, nick i wiadomość

            if len(parts) < 2:
                return

            command = parts[0]

            print(f"Otrzymano komendę: {command} od {nick}")

            if command == "!rec" and len(parts) > 2:
                target_nick, message_content = parts[1], parts[2].strip()
                print(f"Otrzymano komendę !rec od {nick} dla {target_nick} z wiadomością: {message_content}")
                self.handle_rec_command(connection, nick, target_nick, message_content)
            elif command == "!alarm" and len(parts) > 2:
                self.alarm_manager.set_alarm(connection, nick, parts[1:], self.channel)
            elif command == "!minutnik" and len(parts) > 2:
                self.timer_manager.set_timer(connection, nick, parts[1:], self.channel)
            elif command == "!help":
                self.show_help(connection)

    def handle_rec_command(self, connection, sender, target_nick, message):
        """Handle the !rec command to save a message for a user."""
        # Remove any @ or + from the target nick
        target_nick = target_nick.lstrip('@+')
        print(f"Sprawdzanie użytkownika: {target_nick}")

        if self.user_manager.user_exists(target_nick):
            self.message_manager.save_message(sender, target_nick, message)
            connection.privmsg(self.channel, f"{sender}: wiadomość dla {target_nick} zapisana.")
        else:
            connection.privmsg(self.channel, f"{sender}: Użytkownik {target_nick} nie jest obecny na kanale, wiadomość nie została zapisana.")

    def send_saved_messages(self, connection, nick):
        """Send saved messages to a user."""
        # Remove any @ or + from the nick
        nick = nick.lstrip('@+')
        print(f"Sprawdzanie wiadomości dla użytkownika: {nick}")

        if nick in self.message_manager.messages:
            for msg in self.message_manager.messages[nick]:
                print(f"Sending message to {nick}: {msg}")
                connection.privmsg(self.channel, f"{nick}: Wiadomość od {msg['sender']} z {msg['timestamp']}: {msg['message']}")
            del self.message_manager.messages[nick]
            self.message_manager.save_messages()
        else:
            print(f"No messages found for {nick}")

    def show_help(self, connection):
        """Show help message."""
        help_messages = [
            "Dostępne komendy:",
            "!rec <nick> <wiadomość> - Zapisz wiadomość dla użytkownika.",
            "!alarm <HH:MM> <wiadomość> - Ustaw alarm na określoną godzinę z wiadomością.",
            "!minutnik <czas> <wiadomość> - Ustaw minutnik z wiadomością, gdzie czas może być w formacie Xmin lub Xh.",
        ]
        for line in help_messages:
            connection.privmsg(self.channel, line)

    def start_ping_thread(self):
        """Start a thread to send PING to the server to keep the connection alive."""
        def ping():
            while self.keep_running:
                current_time = time.time()
                if self.connection.is_connected():
                    if current_time - self.last_ping_time >= 60:
                        self.connection.ping("keepalive")
                        self.last_ping_time = current_time
                time.sleep(1)

        ping_thread = threading.Thread(target=ping, daemon=True)
        ping_thread.start()

    def on_pong(self, connection, event):
        """Handle PONG responses to keep the connection alive."""
        self.last_ping_time = time.time()

def main():
    server = "127.0.0.1"
    port = 6667
    channel = "#CONTEMPT"
    nickname = "MemoBot"
    bind_address = "127.0.0.1"  # Add the desired bind address here
    bot = NotkaBot(channel, nickname, server, port, bind_address=bind_address)
    bot.start()

if __name__ == "__main__":
    main()
