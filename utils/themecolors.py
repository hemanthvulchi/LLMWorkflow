#store theme colors
colors = {
    'output': '#016FB9',
    'transform': '#CB7301',    
    'input': '#037c6e',
    'danger': '#C1292E',
    'maize': '#F7EF81',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
    'border': '#646464',  # Border color (11, 53, 181)
}

def get_color_hex(color_name):
    return colors.get(color_name, None)

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_color_rgb(color_name):
    hex_color = get_color_hex(color_name)
    if hex_color:
        return hex_to_rgb(hex_color)
    return None

# Usage example
if __name__ == "__main__":
    primary_color_hex = get_color_hex('transform')
    primary_color_rgb = get_color_rgb('transform')
    border_color_hex = get_color_hex('input')
    border_color_rgb = get_color_rgb('input')

    print(f"Primary Color (Hex): {primary_color_hex}")
    print(f"Primary Color (RGB): {primary_color_rgb}")
    print(f"Border Color (Hex): {border_color_hex}")
    print(f"Border Color (RGB): {border_color_rgb}")