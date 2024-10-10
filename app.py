import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import serial

class ModbusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modbus Control Panel")
        
        self.continuous_reading = False

        self.read_count = 0

        # Initialize serial port
        self.ports = list(serial.tools.list_ports.comports())
        self.port_var = tk.StringVar()
        self.baudrate_var = tk.IntVar(value=9600)
        self.stopbits_var = tk.IntVar(value=serial.STOPBITS_ONE)
        self.bytesize_var = tk.IntVar(value=serial.EIGHTBITS)
        self.parity_var = tk.StringVar(value=serial.PARITY_NONE)
        self.slave_id_var = tk.IntVar(value=247)
        self.command_address_var = tk.IntVar()
        self.command_value_var = tk.IntVar()
        self.current_address_var = tk.IntVar(value=247)
        self.new_address_var = tk.IntVar(value=1)
        self.model_var = tk.StringVar(value="Single-phase")

        # Serial port selection
        ttk.Label(root, text="Select Port:").grid(column=0, row=0, padx=10, pady=5)
        self.port_menu = ttk.Combobox(root, textvariable=self.port_var, values=[port.device for port in self.ports])
        self.port_menu.grid(column=1, row=0, padx=10, pady=5)

        # Baud rate selection
        ttk.Label(root, text="Baud Rate:").grid(column=0, row=1, padx=10, pady=5)
        ttk.Combobox(root, textvariable=self.baudrate_var, values=[9600, 19200, 38400, 57600, 115200]).grid(column=1, row=1, padx=10, pady=5)

        # Data bits selection
        ttk.Label(root, text="Data Bits:").grid(column=0, row=2, padx=10, pady=5)
        ttk.Combobox(root, textvariable=self.bytesize_var, values=[serial.FIVEBITS, serial.SIXBITS, serial.SEVENBITS, serial.EIGHTBITS]).grid(column=1, row=2, padx=10, pady=5)

        # Stop bits selection
        ttk.Label(root, text="Stop Bits:").grid(column=0, row=3, padx=10, pady=5)
        ttk.Combobox(root, textvariable=self.stopbits_var, values=[serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO]).grid(column=1, row=3, padx=10, pady=5)

        # Parity selection
        ttk.Label(root, text="Parity:").grid(column=0, row=4, padx=10, pady=5)
        ttk.Combobox(root, textvariable=self.parity_var, values=[serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE]).grid(column=1, row=4, padx=10, pady=5)

        # Slave ID input
        self.slave_id_label = ttk.Label(root, text="Slave ID:")
        self.slave_id_label.grid(column=0, row=5, padx=10, pady=5)

        self.slave_id_spinbox = ttk.Spinbox(root, from_=1, to=247, textvariable=self.slave_id_var, width=5)
        self.slave_id_spinbox.grid(column=1, row=5, padx=10, pady=5)

        # Device model selection
        ttk.Label(root, text="Device Model:").grid(column=0, row=6, padx=10, pady=5)
        ttk.Combobox(root, textvariable=self.model_var, values=["Single-phase", "Two-phase", "Three-phase"]).grid(column=1, row=6, padx=10, pady=5)

        # Connect button
        ttk.Button(root, text="Connect", command=self.connect).grid(column=1, row=7, padx=5, pady=2, sticky='w')

        # Disconnect button
        ttk.Button(root, text="Disconnect", command=self.disconnect).grid(column=1, row=7, padx=5, pady=2, sticky='e')

        # Connection status label
        self.status_label = ttk.Label(root, text="Disconnected", foreground="red")
        self.status_label.grid(column=0, row=7, padx=10, pady=2)

        # Send command
        ttk.Label(root, text="Command Address:").grid(column=0, row=8, padx=10, pady=5)
        ttk.Entry(root, textvariable=self.command_address_var).grid(column=1, row=8, padx=10, pady=5)
        ttk.Label(root, text="Command Value:").grid(column=0, row=9, padx=10, pady=5)
        ttk.Entry(root, textvariable=self.command_value_var).grid(column=1, row=9, padx=10, pady=5)
        ttk.Button(root, text="Send Command", command=self.send_command, width=11).grid(column=0, row=10, columnspan=3, padx=10, pady=5)

        # Change address
        ttk.Label(root, text="Current Slave ID:").grid(column=0, row=11, padx=10, pady=5)
        ttk.Label(root, textvariable=self.current_address_var).grid(column=1, row=11, padx=10, pady=5)
        ttk.Label(root, text="New Slave ID:").grid(column=0, row=12, padx=10, pady=5)
        self.new_slave_id_spinbox = ttk.Spinbox(root, from_=1, to=246, textvariable=self.new_address_var, width=5)
        self.new_slave_id_spinbox.grid(column=1, row=12, padx=10, pady=5)
        ttk.Button(root, text="Change Slave ID", command=self.change_address, width=11).grid(column=0, row=13, columnspan=3, padx=5, pady=5)

        # Read data button
        ttk.Button(root, text="Read Data", command=self.read_data).grid(column=0, row=14, padx=10, pady=5)
        self.toggle_button = ttk.Button(root, text="Auto Read", command=self.toggle_continuous_read)
        self.toggle_button.grid(column=1, row=14, padx=10, pady=5)

        # Display results
        self.result_text = tk.Text(root, width=50, height=15)
        self.result_text.grid(column=0, row=15, columnspan=3, padx=10, pady=1)

        # Add footer label
        self.footer = ttk.Label(root, text="by @Script0803", foreground="blue", cursor="hand2")
        self.footer.grid(column=0, row=16, columnspan=3, pady=1)
        self.footer.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/script0803"))

        self.client = None

    def connect(self):
        if self.client and self.client.is_socket_open():
            messagebox.showinfo("Info", "Already connected")
            return

        port = self.port_var.get()
        slave_id = self.slave_id_var.get()

        if not port:
            messagebox.showerror("Error", "Please select a port")
            return

        self.client = ModbusSerialClient(
            port=port,
            baudrate=self.baudrate_var.get(),
            stopbits=self.stopbits_var.get(),
            bytesize=self.bytesize_var.get(),
            parity=self.parity_var.get(),
            timeout=1
        )

        if self.client.connect():
            messagebox.showinfo("Success", "Connected successfully")
            self.current_address_var.set(slave_id)
            self.status_label.config(text="Connected", foreground="green")
            self.read_count = 0
        else:
            messagebox.showerror("Error", "Unable to connect to Modbus device")
            self.status_label.config(text="Disconnected", foreground="red")

    def disconnect(self):
        if self.client:
            self.client.close()
            messagebox.showinfo("Success", "Disconnected")
            self.status_label.config(text="Disconnected", foreground="red")

    def send_custom_command(self):
        address = self.command_address_var.get()
        value = self.command_value_var.get()
        self.send_command(address, value)

    def send_command(self, address, value):
        if self.client:
            result = self.client.write_register(address, value, slave=self.slave_id_var.get())
            if not result.isError():
                messagebox.showinfo("Success", f"Command sent successfully: Address {address}, Value {value}")
            else:
                messagebox.showerror("Error", f"Command failed: {result}")

    def change_address(self):
        new_address = self.new_address_var.get()
        if 1 <= new_address <= 247:
            self.send_command(6000, new_address)
            self.current_address_var.set(new_address)
        else:
            messagebox.showerror("Error", "Invalid Modbus address")

    def read_float_register(self, address):
        if self.client:
            try:
                count = 2
                result = self.client.read_holding_registers(address, count, slave=self.slave_id_var.get())
                if not result.isError():
                    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
                    return decoder.decode_32bit_float()
                else:
                    return None
            except Exception as e:
                messagebox.showerror("Error", f"Exception occurred: {e}")
                return None

    def read_data(self):
        model = self.model_var.get()
        data_points = self.get_data_points(model)

        self.result_text.delete(1.0, tk.END)

        self.read_count += 1
        self.result_text.insert(tk.END, f"Read Count: {self.read_count}\n")

        for name, address in data_points.items():
            value = self.read_float_register(address)
            if value is None:
                messagebox.showerror("Error", f"Failed to read data. Stopping reads.")
                break
            self.result_text.insert(tk.END, f"{name}: {value}\n")
    
    def toggle_continuous_read(self):
        self.continuous_reading = not self.continuous_reading
        if self.continuous_reading:
            self.read_data_continuously()
            self.toggle_button.config(text="Stop Read")
        else:
            self.toggle_button.config(text="Auto Read")

    def read_data_continuously(self):
        if self.continuous_reading:
            self.read_data()
            self.root.after(1000, self.read_data_continuously)
    
    def get_data_points(self, model):
        if model == "Single-phase":
            return {
                "Voltage": 1000,
                "Current": 1006,
                "Active Power": 1012,
                "Apparent Power": 1024,
                "Power Factor": 1030,
                "Frequency": 1052,
                "Total Import Active Energy": 1054,
                "Total Import Export Energy": 1056
            }
        elif model == "Two-phase":
            return {
                "Voltage L1": 1000,
                "Voltage L2": 1002,
                "Current L1": 1006,
                "Current L2": 1008,
                "Active Power L1": 1012,
                "Active Power L2": 1014,
                "Reactive Power L1": 1018,
                "Reactive Power L2": 1020,
                "Apparent Power L1": 1024,
                "Apparent Power L2": 1026,
                "Power Factor L1": 1030,
                "Power Factor L2": 1032,
                "Frequency": 1052,
                "Total Import Active Energy": 1054,
                "Total Import Export Energy": 1056,
                "Total Import and Export Active Energy": 1058,
                "Phase L1 Import Active Energy": 1060,
                "Phase L1 Export Active Energy": 1062,
                "Phase L1 Import and Export Active Energy": 1064,
                "Phase L2 Import Active Energy": 1066,
                "Phase L2 Export Active Energy": 1068,
                "Phase L2 Import and Export Active Energy": 1070
            }
        elif model == "Three-phase":
            return {
                "Voltage A": 1000,
                "Voltage B": 1002,
                "Voltage C": 1004,
                "Current A": 1006,
                "Current B": 1008,
                "Current C": 1010,
                "Active Power A": 1012,
                "Active Power B": 1014,
                "Active Power C": 1016,
                "Reactive Power A": 1018,
                "Reactive Power B": 1020,
                "Reactive Power C": 1022,
                "Apparent Power A": 1024,
                "Apparent Power B": 1026,
                "Apparent Power C": 1028,
                "Power Factor A": 1030,
                "Power Factor B": 1032,
                "Power Factor C": 1034,
                "Frequency": 1052,
                "Total Import Active Energy": 1054,
                "Total Import Export Energy": 1056,
                "Total Import and Export Active Energy": 1058,
                "Phase A Import Active Energy": 1060,
                "Phase A Export Active Energy": 1062,
                "Phase A Import and Export Active Energy": 1064,
                "Phase B Import Active Energy": 1066,
                "Phase B Export Active Energy": 1068,
                "Phase B Import and Export Active Energy": 1070,
                "Phase C Import Active Energy": 1072,
                "Phase C Export Active Energy": 1074,
                "Phase C Import and Export Active Energy": 1076
            }

if __name__ == "__main__":
    root = tk.Tk()
    app = ModbusApp(root)
    root.mainloop()
