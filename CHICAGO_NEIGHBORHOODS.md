# Chicago Neighborhoods Guide

This guide lists popular Chicago neighborhoods that you can use in your `config.json` file.

## How to Use

In your `config.json`, add neighborhoods to the `neighborhoods` array:

```json
{
  "search_criteria": {
    "location": "Chicago, IL",
    "neighborhoods": ["lincoln-park", "wicker-park", "logan-square"],
    ...
  }
}
```

**Note**: Use the slug format (lowercase, hyphens instead of spaces).

## Popular Chicago Neighborhoods

### North Side

| Neighborhood | Slug | Description |
|--------------|------|-------------|
| Lincoln Park | `lincoln-park` | Upscale, family-friendly, near lake |
| Lakeview | `lakeview` | Diverse, near Wrigley Field |
| Wrigleyville | `wrigleyville` | Nightlife, Cubs fans, young professionals |
| Andersonville | `andersonville` | Charming, Swedish heritage, LGBTQ+ friendly |
| Uptown | `uptown` | Cultural diversity, entertainment venues |
| Edgewater | `edgewater` | Quiet, lakefront, diverse community |
| Rogers Park | `rogers-park` | Affordable, diverse, beach access |
| Ravenswood | `ravenswood` | Quiet residential, families |
| North Center | `north-center` | Family-friendly, quiet streets |

### Northwest Side

| Neighborhood | Slug | Description |
|--------------|------|-------------|
| Wicker Park | `wicker-park` | Trendy, arts scene, nightlife |
| Bucktown | `bucktown` | Hip, boutiques, young professionals |
| Logan Square | `logan-square` | Artistic, diverse, restaurants |
| Avondale | `avondale` | Up-and-coming, affordable |
| Irving Park | `irving-park` | Residential, families, affordable |
| Old Town | `old-town` | Historic, charming, walkable |
| Ukrainian Village | `ukrainian-village` | Artistic, affordable, diverse |
| Humboldt Park | `humboldt-park` | Cultural, park access, affordable |

### West Side

| Neighborhood | Slug | Description |
|--------------|------|-------------|
| West Loop | `west-loop` | Trendy, restaurants, new developments |
| Near West Side | `near-west-side` | Growing, medical district nearby |
| University Village | `university-village` | Student-friendly, near UIC |
| Little Italy | `little-italy` | Cultural, historic, restaurants |
| Pilsen | `pilsen` | Arts, Mexican culture, murals |
| West Town | `west-town` | Trendy, diverse, nightlife |

### Downtown / Central

| Neighborhood | Slug | Description |
|--------------|------|-------------|
| The Loop | `loop` | Business district, central |
| River North | `river-north` | Art galleries, restaurants, nightlife |
| Streeterville | `streeterville` | Upscale, near lake and Navy Pier |
| Gold Coast | `gold-coast` | Luxury, historic mansions, shopping |
| Magnificent Mile | `magnificent-mile` | Shopping, hotels, upscale |
| South Loop | `south-loop` | Growing residential, museums |
| West Loop | `west-loop` | Trendy restaurants, tech startups |
| Near North Side | `near-north-side` | Central, diverse, mixed-use |

### South Side

| Neighborhood | Slug | Description |
|--------------|------|-------------|
| Bronzeville | `bronzeville` | Historic, cultural, growing |
| Hyde Park | `hyde-park` | Academic (UChicago), cultural |
| Bridgeport | `bridgeport` | Working-class, White Sox territory |
| Chinatown | `chinatown` | Cultural, restaurants, shopping |
| Kenwood | `kenwood` | Historic mansions, quiet |
| South Shore | `south-shore` | Lakefront, residential |
| Woodlawn | `woodlawn` | Near university, developing |

## Finding More Neighborhoods

To find additional neighborhoods or verify slugs:

1. Visit Apartments.com: https://www.apartments.com/chicago-il/
2. Look for neighborhood links or filters
3. Click on a neighborhood
4. Check the URL format: `https://www.apartments.com/chicago-il/{neighborhood-slug}/`

## Example Configurations

### Target specific trendy areas:
```json
"neighborhoods": ["wicker-park", "logan-square", "west-loop"]
```

### North Side only:
```json
"neighborhoods": ["lincoln-park", "lakeview", "andersonville", "ravenswood"]
```

### Budget-friendly options:
```json
"neighborhoods": ["rogers-park", "avondale", "pilsen", "bridgeport"]
```

### Leave empty for entire Chicago:
```json
"neighborhoods": []
```

## Tips

- **Start broad**: Test with 1-2 neighborhoods first to see what you get
- **Refine**: Add more neighborhoods if you're not getting enough results
- **Be specific**: Neighborhood filtering gives more relevant results than city-wide searches
- **Multiple pages**: With multiple neighborhoods, consider using `--pages 2` for more results per neighborhood
