// Internal-assembly documentation views (v0.8.3c) — composites the CadQuery STLs.
// Usage: openscad -D 'view="pod_deck"' (pod_deck | cart_module | pod_rfid | bay | bay_tray)
view = "pod_deck";

module electronics_colors() {}

module cart_module() {
    color("#D95D39") import("../stl/pedestal_cart.stl");        // ORANGE = pedestal cart
    color("#9AA0A8") import("../stl/mock_solenoid.stl");
    color("#22703A") import("../stl/mock_driver_stack.stl");
    color("#22703A") import("../stl/mock_mt3608.stl");
}

module pod_deck() {
    color("#5A748C") import("../stl/body.stl");
    cart_module();
    color("#C8A24B") import("../stl/mock_cable_head.stl");
    color("#22703A") import("../stl/mock_nano.stl");
    color("#D95D39") import("../stl/nano_clamp.stl");
    color("#8A2F2F") import("../stl/mock_led.stl");
}

module pod_rfid() {
    pod_deck();
    color("#22703A") import("../stl/mock_pn532.stl");
    color("#3B3B3B") import("../stl/mock_button.stl");
    %color("#C8CDD2") translate([0, 0, 14]) import("../stl/lid.stl");  // lid ghosted, lifted 14
}

module bay() {
    color("#22303C") import("../stl/bay_module.stl");
    color("#22703A") import("../stl/mock_tp4056.stl");
    color("#B8BDC4") import("../stl/mock_lipo.stl");
}

module bay_tray() {
    bay();
    color("#455A64") translate([4, 27.5, -73]) import("../stl/bay_hatch.stl");  // dropped 12 for view
}

if (view == "pod_deck") pod_deck();
if (view == "cart_module") cart_module();
if (view == "pod_rfid") pod_rfid();
if (view == "bay") bay();
if (view == "bay_tray") bay_tray();
