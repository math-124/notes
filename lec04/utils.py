import plotly.graph_objects as go
import numpy as np

FONT_FAMILY = "Palatino"

def plot_vectors(vectors, title=None, font=None, xaxis_title='x', yaxis_title='y', zaxis_title='z', vdeltax=0.3, vdeltay=0.3, vdeltaz=0.3, show_axis_labels=None):
    """
    Plot a list of vectors in 2D or 3D space.
    
    Args:
        vectors: List of tuples in format [(coordinates, color, label), ...]
                where coordinates is a tuple of 2D or 3D coordinates,
                color is a string color name, and label is a string label
        title: Optional title for the plot
        font: Optional font dictionary (e.g., dict(family="Arial", size=14, color="black"))
        xaxis_title: Title for x-axis (default: 'x')
        yaxis_title: Title for y-axis (default: 'y') 
        zaxis_title: Title for z-axis (default: 'z', only used in 3D)
        vdeltax: Horizontal offset for label positioning above vector midpoints (default: 0.3)
        vdeltay: Vertical offset for label positioning above vector midpoints (default: 0.3)
        vdeltaz: Vertical offset for label positioning above vector midpoints (default: 0.3)
        show_axis_labels: Whether to show axis labels (None=auto: False for 2D, True for 3D)
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    if not vectors:
        raise ValueError("Vector list cannot be empty")
    
    # Validate dimensions are consistent
    dimensions = set()
    for vector_data in vectors:
        if len(vector_data) != 3:
            raise ValueError("Each vector must be a tuple of (coordinates, color, label)")
        
        coordinates, color, label = vector_data
        if not isinstance(coordinates, (tuple, list)):
            raise ValueError("Coordinates must be a tuple or list")
        
        dim = len(coordinates)
        if dim not in [2, 3]:
            raise ValueError("Coordinates must be 2D or 3D")
        
        dimensions.add(dim)
    
    if len(dimensions) > 1:
        raise ValueError("All vectors must have the same dimension (all 2D or all 3D)")
    
    dimension = dimensions.pop()
    
    # Set default axis label visibility based on dimension
    if show_axis_labels is None:
        show_axis_labels = (dimension == 3)  # False for 2D, True for 3D
    
    if dimension == 2:
        return plot_vectors_2d(vectors, title=title, font=font, xaxis_title=xaxis_title, yaxis_title=yaxis_title, vdeltax=vdeltax, vdeltay=vdeltay, show_axis_labels=show_axis_labels)
    else:
        return plot_vectors_3d(vectors, title=title, font=font, xaxis_title=xaxis_title, yaxis_title=yaxis_title, zaxis_title=zaxis_title, vdeltax=vdeltax, vdeltay=vdeltay, vdeltaz=vdeltaz, show_axis_labels=show_axis_labels)

def plot_vectors_2d(vectors, title=None, font=None, xaxis_title='x', yaxis_title='y', vdeltax=0.3, vdeltay=0.3, show_axis_labels=False):
    """
    Plot vectors in 2D space with labels rotated along vector direction.
    
    Args:
        vectors: List of tuples in format [(coordinates, color, label), ...]
        title: Optional title for the plot
        font: Optional font dictionary
        xaxis_title: Title for x-axis
        yaxis_title: Title for y-axis
        vdeltax: Horizontal offset for label positioning above vector midpoints
        vdeltay: Vertical offset for label positioning above vector midpoints
        vdeltaz: Vertical offset for label positioning above vector midpoints
        show_axis_labels: Whether to show axis labels
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    fig = go.Figure()
    
    # Set default font if none provided and extract font size
    if font is None:
        font = dict(family=FONT_FAMILY, size=14, color="black")
        label_font_size = 16
    else:
        label_font_size = font.get('size', 14)
    
    # Collect all coordinates for range calculation
    all_coords = []
    
    for coordinates, color, label in vectors:
        x, y = coordinates
        all_coords.extend([x, y, 0])  # Include origin
        
        # Draw vector with arrow tip using lines+markers approach
        fig.add_trace(go.Scatter(
            x=[0, x], 
            y=[0, y],
            mode='lines+markers',
            line=dict(color=color, width=4),
            marker=dict(
                size=[0, 16],  # No marker at start, smaller arrow at end
                color=[color, color],  # Same color for both points
                symbol=['circle', 'arrow'],
                angleref='previous'
            ),
            hovertemplate='(%{x}, %{y})<extra></extra>',
            showlegend=False
        ))
        
        # Add label at midpoint, rotated along vector direction
        mid_x, mid_y = x/2, y/2
        
        # Calculate angle of vector in degrees
        vector_angle = np.degrees(np.arctan2(y, x))
        
        # Adjust angle for better readability (avoid upside-down text)
        if vector_angle > 90:
            vector_angle -= 180
        elif vector_angle < -90:
            vector_angle += 180
        
        # Calculate perpendicular offset for label positioning
        vector_length = np.sqrt(x**2 + y**2)
        if vector_length > 0:
            # Unit perpendicular vector (rotated 90 degrees)
            perp_x = -y / vector_length
            perp_y = x / vector_length
            # Apply offset
            label_x = mid_x + perp_x * vdeltax
            label_y = mid_y + perp_y * vdeltay
        else:
            label_x, label_y = mid_x, mid_y + vdeltay
        
        fig.add_trace(go.Scatter(
            x=[label_x], 
            y=[label_y],
            mode='text',
            text=[label],
            textposition='middle center',
            textfont=dict(size=label_font_size, color=color, family=FONT_FAMILY),
            hoverinfo='skip',
            showlegend=False
        ))
        
        # Add invisible annotation for rotated text effect
        fig.add_annotation(
            x=label_x,
            y=label_y,
            text=label,
            showarrow=False,
            font=dict(size=label_font_size, color=color, family=FONT_FAMILY),
            # textangle=vector_angle,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0)",
            borderwidth=0
        )
    
    # Remove the regular text traces since we're using annotations
    fig.data = [trace for trace in fig.data if trace.mode != 'text']
    
    # Calculate axis ranges
    coords = [coord for coordinates, _, _ in vectors for coord in coordinates] + [0]
    coord_range = [min(coords) - 1, max(coords) + 1]
    
    # Update layout
    layout_dict = dict(
        xaxis=dict(
            title=xaxis_title if show_axis_labels else '',
            range=coord_range,
            gridcolor='#f0f0f0',
            zerolinecolor='gray',
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title=yaxis_title if show_axis_labels else '',
            range=coord_range,
            gridcolor='#f0f0f0',
            zerolinecolor='gray',
            tickfont=dict(size=10)
        ),
        width=800,
        height=600,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=font,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # Add title if provided
    if title is not None:
        layout_dict['title'] = title
    
    fig.update_layout(layout_dict)
    
    return fig

def plot_vectors_3d(vectors, title=None, font=None, xaxis_title='x', yaxis_title='y', zaxis_title='z', vdeltax=0.3, vdeltay=0.3, vdeltaz=0.3, show_axis_labels=True):
    """
    Plot vectors in 3D space.
    Note: 3D text rotation is limited in Plotly, so labels remain horizontal but positioned along vectors.
    
    Args:
        vectors: List of tuples in format [(coordinates, color, label), ...]
        title: Optional title for the plot
        font: Optional font dictionary
        xaxis_title: Title for x-axis
        yaxis_title: Title for y-axis
        zaxis_title: Title for z-axis
        vdeltax: Horizontal offset for label positioning above vector midpoints
        vdeltay: Vertical offset for label positioning above vector midpoints
        vdeltaz: Vertical offset for label positioning above vector midpoints
        show_axis_labels: Whether to show axis labels
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    fig = go.Figure()
    
    # Set default font if none provided and extract font size
    if font is None:
        font = dict(family=FONT_FAMILY, size=14, color="black")
        label_font_size = 16
    else:
        label_font_size = font.get('size', 14)
    
    for coordinates, color, label in vectors:
        x, y, z = coordinates
        
        # Draw vector line
        fig.add_trace(go.Scatter3d(
            x=[0, x], 
            y=[0, y], 
            z=[0, z],
            mode='lines',
            line=dict(color=color, width=6),
            hovertemplate='(%{x}, %{y}, %{z})<extra></extra>',
            showlegend=False
        ))
        
        # Add arrow tip using cone
        fig.add_trace(go.Cone(
            x=[x], 
            y=[y], 
            z=[z],
            u=[x/10],  # Direction scaled down for cone size control
            v=[y/10], 
            w=[z/10],
            sizemode="raw",
            sizeref=0.4,
            colorscale=[[0, color], [1, color]],  # Single color
            showscale=False,
            hoverinfo='skip',
            showlegend=False
        ))
        
        # Add label positioned along the vector at midpoint
        # Note: 3D text rotation is limited in Plotly, so we position along the vector
        mid_x, mid_y, mid_z = x/2, y/2, z/2
        
        # For 3D, we'll position the label directly on the vector line
        # with a slight offset for visibility
        vector_length = np.sqrt(x**2 + y**2 + z**2)
        if vector_length > 0:
            # Create a small offset perpendicular to the vector
            # Use cross product with a reference vector to get perpendicular direction
            ref_vector = np.array([0, 0, 1])  # Use z-axis as reference
            vector_norm = np.array([x, y, z]) / vector_length
            
            # If vector is parallel to z-axis, use y-axis as reference
            if abs(np.dot(vector_norm, ref_vector)) > 0.9:
                ref_vector = np.array([0, 1, 0])
            
            # Get perpendicular vector
            perp_vector = np.cross(vector_norm, ref_vector)
            perp_vector = perp_vector / np.linalg.norm(perp_vector)
            
            # Apply small offset
            # offset_scale = vdeltax * 0.5
            label_x = mid_x + perp_vector[0] * vdeltax * 0.5
            label_y = mid_y + perp_vector[1] * vdeltay * 0.5
            label_z = mid_z + perp_vector[2] * vdeltaz * 0.5
        else:
            label_x, label_y, label_z = mid_x + vdeltax, mid_y + vdeltay, mid_z + vdeltaz
        
        fig.add_trace(go.Scatter3d(
            x=[label_x], 
            y=[label_y], 
            z=[label_z],
            mode='text',
            text=[label],
            textposition='middle center',
            textfont=dict(size=label_font_size, color=color, family=FONT_FAMILY),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Calculate axis ranges
    all_vectors = [coordinates for coordinates, _, _ in vectors]
    x_coords = [v[0] for v in all_vectors] + [0]
    y_coords = [v[1] for v in all_vectors] + [0]
    z_coords = [v[2] for v in all_vectors] + [0]
    
    x_range = [min(x_coords) - 1, max(x_coords) + 1]
    y_range = [min(y_coords) - 1, max(y_coords) + 1]
    z_range = [min(z_coords) - 1, max(z_coords) + 1]
    
    # Update layout
    layout_dict = dict(
        scene=dict(
            xaxis=dict(
                title=xaxis_title if show_axis_labels else '',
                backgroundcolor='white',
                gridcolor='#f0f0f0',
                showbackground=True,
                zerolinecolor='gray',
                range=x_range,
                tickfont=dict(size=10)
            ),
            yaxis=dict(
                title=yaxis_title if show_axis_labels else '',
                backgroundcolor='white',
                gridcolor='#f0f0f0',
                showbackground=True,
                zerolinecolor='gray',
                range=y_range,
                tickfont=dict(size=10)
            ),
            zaxis=dict(
                title=zaxis_title if show_axis_labels else '',
                backgroundcolor='white',
                gridcolor='#f0f0f0',
                showbackground=True,
                zerolinecolor='gray',
                range=z_range,
                tickfont=dict(size=10)
            ),
            bgcolor='white',
            camera=dict(
                eye=dict(x=1.25, y=2, z=0.25)
            ),
            aspectratio=dict(x=1.2, y=1.2, z=0.8)
        ),
        width=800,
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=font,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    # Add title if provided
    if title is not None:
        layout_dict['title'] = title
    
    fig.update_layout(layout_dict)
    
    return fig

def plot_vectors_non_origin(vectors, title=None, font=None, xaxis_title='x', yaxis_title='y', zaxis_title='z', vdeltax=0.3, vdeltay=0.3, vdeltaz=0.3, show_axis_labels=None):
    """
    Plot a list of vectors in 2D or 3D space that can start from arbitrary points (not just origin).
    
    Args:
        vectors: List of tuples in format [((start_coords, end_coords), color, label), ...]
                where start_coords and end_coords are tuples of 2D or 3D coordinates,
                color is a string color name, and label is a string label
        title: Optional title for the plot
        font: Optional font dictionary (e.g., dict(family="Arial", size=14, color="black"))
        xaxis_title: Title for x-axis (default: 'x')
        yaxis_title: Title for y-axis (default: 'y') 
        zaxis_title: Title for z-axis (default: 'z', only used in 3D)
        vdeltax: Horizontal offset for label positioning above vector midpoints (default: 0.3)
        vdeltay: Vertical offset for label positioning above vector midpoints (default: 0.3)
        vdeltaz: Vertical offset for label positioning above vector midpoints (default: 0.3)
        show_axis_labels: Whether to show axis labels (None=auto: False for 2D, True for 3D)
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    if not vectors:
        raise ValueError("Vector list cannot be empty")
    
    # Validate dimensions are consistent
    dimensions = set()
    for vector_data in vectors:
        if len(vector_data) != 3:
            raise ValueError("Each vector must be a tuple of ((start_coords, end_coords), color, label)")
        
        coord_pair, color, label = vector_data
        if not isinstance(coord_pair, (tuple, list)) or len(coord_pair) != 2:
            raise ValueError("First element must be a tuple/list of (start_coords, end_coords)")
        
        start_coords, end_coords = coord_pair
        
        if not isinstance(start_coords, (tuple, list)) or not isinstance(end_coords, (tuple, list)):
            raise ValueError("Start and end coordinates must be tuples or lists")
        
        if len(start_coords) != len(end_coords):
            raise ValueError("Start and end coordinates must have the same dimension")
        
        dim = len(start_coords)
        if dim not in [2, 3]:
            raise ValueError("Coordinates must be 2D or 3D")
        
        dimensions.add(dim)
    
    if len(dimensions) > 1:
        raise ValueError("All vectors must have the same dimension (all 2D or all 3D)")
    
    dimension = dimensions.pop()
    
    # Set default axis label visibility based on dimension
    if show_axis_labels is None:
        show_axis_labels = (dimension == 3)  # False for 2D, True for 3D
    
    if dimension == 2:
        return plot_vectors_non_origin_2d(vectors, title=title, font=font, xaxis_title=xaxis_title, yaxis_title=yaxis_title, vdeltax=vdeltax, vdeltay=vdeltay, show_axis_labels=show_axis_labels)
    else:
        return plot_vectors_non_origin_3d(vectors, title=title, font=font, xaxis_title=xaxis_title, yaxis_title=yaxis_title, zaxis_title=zaxis_title, vdeltax=vdeltax, vdeltay=vdeltay, vdeltaz=vdeltaz, show_axis_labels=show_axis_labels)

def plot_vectors_non_origin_2d(vectors, title=None, font=None, xaxis_title='x', yaxis_title='y', vdeltax=0.3, vdeltay=0.3, show_axis_labels=False):
    """
    Plot vectors in 2D space that can start from arbitrary points.
    
    Args:
        vectors: List of tuples in format [((start_coords, end_coords), color, label), ...]
        title: Optional title for the plot
        font: Optional font dictionary
        xaxis_title: Title for x-axis
        yaxis_title: Title for y-axis
        vdeltax: Horizontal offset for label positioning above vector midpoints
        vdeltay: Vertical offset for label positioning above vector midpoints
        show_axis_labels: Whether to show axis labels
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    fig = go.Figure()
    
    # Set default font if none provided and extract font size
    if font is None:
        font = dict(family=FONT_FAMILY, size=14, color="black")
        label_font_size = 16
    else:
        label_font_size = font.get('size', 14)
    
    # Collect all coordinates for range calculation
    all_coords = []
    
    for coord_pair, color, label in vectors:
        start_coords, end_coords = coord_pair
        start_x, start_y = start_coords
        end_x, end_y = end_coords
        
        all_coords.extend([start_x, start_y, end_x, end_y])
        
        # Draw vector with arrow tip using lines+markers approach
        fig.add_trace(go.Scatter(
            x=[start_x, end_x], 
            y=[start_y, end_y],
            mode='lines+markers',
            line=dict(color=color, width=4),
            marker=dict(
                size=[0, 16],  # No marker at start, smaller arrow at end
                color=[color, color],  # Same color for both points
                symbol=['circle', 'arrow'],
                angleref='previous'
            ),
            hovertemplate='(%{x}, %{y})<extra></extra>',
            showlegend=False
        ))
        
        # Add label at midpoint
        mid_x, mid_y = (start_x + end_x) / 2, (start_y + end_y) / 2
        
        # Calculate vector direction for perpendicular offset
        vec_x, vec_y = end_x - start_x, end_y - start_y
        vector_length = np.sqrt(vec_x**2 + vec_y**2)
        
        if vector_length > 0:
            # Unit perpendicular vector (rotated 90 degrees)
            perp_x = -vec_y / vector_length
            perp_y = vec_x / vector_length
            # Apply offset
            label_x = mid_x + perp_x * vdeltax
            label_y = mid_y + perp_y * vdeltay
        else:
            label_x, label_y = mid_x, mid_y + vdeltay
        
        # Add annotation for the label
        fig.add_annotation(
            x=label_x,
            y=label_y,
            text=label,
            showarrow=False,
            font=dict(size=label_font_size, color=color, family=FONT_FAMILY),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0)",
            borderwidth=0
        )
    
    # Calculate axis ranges
    coord_range = [min(all_coords) - 1, max(all_coords) + 1]
    
    # Update layout
    layout_dict = dict(
        xaxis=dict(
            title=xaxis_title if show_axis_labels else '',
            range=coord_range,
            gridcolor='#f0f0f0',
            zerolinecolor='gray',
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title=yaxis_title if show_axis_labels else '',
            range=coord_range,
            gridcolor='#f0f0f0',
            zerolinecolor='gray',
            tickfont=dict(size=10)
        ),
        width=800,
        height=600,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=font,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # Add title if provided
    if title is not None:
        layout_dict['title'] = title
    
    fig.update_layout(layout_dict)
    
    return fig

def plot_vectors_non_origin_3d(vectors, title=None, font=None, xaxis_title='x', yaxis_title='y', zaxis_title='z', vdeltax=0.3, vdeltay=0.3, vdeltaz=0.3, show_axis_labels=True):
    """
    Plot vectors in 3D space that can start from arbitrary points.
    
    Args:
        vectors: List of tuples in format [((start_coords, end_coords), color, label), ...]
        title: Optional title for the plot
        font: Optional font dictionary
        xaxis_title: Title for x-axis
        yaxis_title: Title for y-axis
        zaxis_title: Title for z-axis
        vdeltax: Horizontal offset for label positioning above vector midpoints
        vdeltay: Vertical offset for label positioning above vector midpoints
        vdeltaz: Vertical offset for label positioning above vector midpoints
        show_axis_labels: Whether to show axis labels
    
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    fig = go.Figure()
    
    # Set default font if none provided and extract font size
    if font is None:
        font = dict(family=FONT_FAMILY, size=14, color="black")
        label_font_size = 16
    else:
        label_font_size = font.get('size', 14)
    
    # Collect all coordinates for range calculation
    all_coords = {'x': [], 'y': [], 'z': []}
    
    for coord_pair, color, label in vectors:
        start_coords, end_coords = coord_pair
        start_x, start_y, start_z = start_coords
        end_x, end_y, end_z = end_coords
        
        all_coords['x'].extend([start_x, end_x])
        all_coords['y'].extend([start_y, end_y])
        all_coords['z'].extend([start_z, end_z])
        
        # Draw vector line
        fig.add_trace(go.Scatter3d(
            x=[start_x, end_x], 
            y=[start_y, end_y], 
            z=[start_z, end_z],
            mode='lines',
            line=dict(color=color, width=6),
            hovertemplate='(%{x}, %{y}, %{z})<extra></extra>',
            showlegend=False
        ))
        
        # Add arrow tip using cone
        # Calculate direction vector
        vec_x, vec_y, vec_z = end_x - start_x, end_y - start_y, end_z - start_z
        
        fig.add_trace(go.Cone(
            x=[end_x], 
            y=[end_y], 
            z=[end_z],
            u=[vec_x/10],  # Direction scaled down for cone size control
            v=[vec_y/10], 
            w=[vec_z/10],
            sizemode="raw",
            sizeref=0.4,
            colorscale=[[0, color], [1, color]],  # Single color
            showscale=False,
            hoverinfo='skip',
            showlegend=False
        ))
        
        # Add label at midpoint
        mid_x, mid_y, mid_z = (start_x + end_x) / 2, (start_y + end_y) / 2, (start_z + end_z) / 2
        
        # Calculate vector direction for offset
        vec_x, vec_y, vec_z = end_x - start_x, end_y - start_y, end_z - start_z
        vector_length = np.sqrt(vec_x**2 + vec_y**2 + vec_z**2)
        
        if vector_length > 0:
            # Create a small offset perpendicular to the vector
            ref_vector = np.array([0, 0, 1])  # Use z-axis as reference
            vector_norm = np.array([vec_x, vec_y, vec_z]) / vector_length
            
            # If vector is parallel to z-axis, use y-axis as reference
            if abs(np.dot(vector_norm, ref_vector)) > 0.9:
                ref_vector = np.array([0, 1, 0])
            
            # Get perpendicular vector
            perp_vector = np.cross(vector_norm, ref_vector)
            perp_vector = perp_vector / np.linalg.norm(perp_vector)
            
            # Apply small offset
            offset_scale = vdeltax * 0.5
            label_x = mid_x + perp_vector[0] * offset_scale
            label_y = mid_y + perp_vector[1] * offset_scale
            label_z = mid_z + perp_vector[2] * offset_scale
        else:
            label_x, label_y, label_z = mid_x + vdeltax, mid_y + vdeltay, mid_z + vdeltaz
        
        fig.add_trace(go.Scatter3d(
            x=[label_x], 
            y=[label_y], 
            z=[label_z],
            mode='text',
            text=[label],
            textposition='middle center',
            textfont=dict(size=label_font_size, color=color, family=FONT_FAMILY),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Calculate axis ranges
    x_range = [min(all_coords['x']) - 1, max(all_coords['x']) + 1]
    y_range = [min(all_coords['y']) - 1, max(all_coords['y']) + 1]
    z_range = [min(all_coords['z']) - 1, max(all_coords['z']) + 1]
    
    # Update layout
    layout_dict = dict(
        scene=dict(
            xaxis=dict(
                title=xaxis_title if show_axis_labels else '',
                backgroundcolor='white',
                gridcolor='#f0f0f0',
                showbackground=True,
                zerolinecolor='gray',
                range=x_range,
                tickfont=dict(size=10)
            ),
            yaxis=dict(
                title=yaxis_title if show_axis_labels else '',
                backgroundcolor='white',
                gridcolor='#f0f0f0',
                showbackground=True,
                zerolinecolor='gray',
                range=y_range,
                tickfont=dict(size=10)
            ),
            zaxis=dict(
                title=zaxis_title if show_axis_labels else '',
                backgroundcolor='white',
                gridcolor='#f0f0f0',
                showbackground=True,
                zerolinecolor='gray',
                range=z_range,
                tickfont=dict(size=10)
            ),
            bgcolor='white',
            camera=dict(
                eye=dict(x=1.25, y=2, z=0.25)
            ),
            aspectratio=dict(x=1.2, y=1.2, z=0.8)
        ),
        width=800,
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=font,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    # Add title if provided
    if title is not None:
        layout_dict['title'] = title
    
    fig.update_layout(layout_dict)
    
    return fig

# Example usage (uncomment to test):
if __name__ == "__main__":
    # 3D example
    vectors_3d = [
        ((3, 1, 4), "black", "row 1"),
        ((2, 1, 9), "black", "row 2"), 
        ((0, -1, 0), "black", "row 3"),
        ((2, -2, 0), "black", "row 4"),
        ((1, 0, 3), "purple", "v")
    ]
    fig = plot_vectors(vectors_3d)
    fig.show()
    
    # 2D example
    vectors_2d = [
        ((2, 3), "red", "v1"),
        ((1, -2), "blue", "v2"),
        ((-1, 1), "green", "v3")
    ]
    fig = plot_vectors(vectors_2d)
    fig.show()
    
    # Non-origin 2D example
    vectors_non_origin_2d = [
        (((1, 1), (3, 4)), "red", "v1"),     # Vector from (1,1) to (3,4)
        (((0, 2), (1, 0)), "blue", "v2"),    # Vector from (0,2) to (1,0)
        (((2, 0), (1, 1)), "green", "v3")    # Vector from (2,0) to (1,1)
    ]
    fig = plot_vectors_non_origin(vectors_non_origin_2d)
    fig.show()
    
    # Non-origin 3D example
    vectors_non_origin_3d = [
        (((1, 1, 1), (4, 2, 5)), "black", "v1"),    # Vector from (1,1,1) to (4,2,5)
        (((0, 0, 2), (2, 1, 11)), "black", "v2"),   # Vector from (0,0,2) to (2,1,11)
        (((2, 1, 0), (2, 0, 0)), "purple", "v3")    # Vector from (2,1,0) to (2,0,0)
    ]
    fig = plot_vectors_non_origin(vectors_non_origin_3d)
    fig.show()