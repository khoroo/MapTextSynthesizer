/*
  A program that lists all the available font families in your system.

  !IMPORTANT!
  This file is the intellectual property of Ben Bullock. Please see source at:
  https://www.lemoda.net/pango/list-fonts/index.html
 */

#include <glib.h>
#include <pango/pangocairo.h>

static void
list_fonts ()
{
    int i;
    PangoFontFamily ** families;
    int n_families;
    PangoFontMap * fontmap;

    fontmap = pango_cairo_font_map_get_default();
    pango_font_map_list_families (fontmap, & families, & n_families);
    printf ("There are %d families\n", n_families);
    for (i = 0; i < n_families; i++) {
        PangoFontFamily * family = families[i];
        const char * family_name;

        family_name = pango_font_family_get_name (family);
        printf ("%s\n", family_name);
    }
    g_free (families);
}

int main (int argc, char ** argv)
{
    list_fonts ();
    return 0;
}
