# pylint: disable=too-many-branches,too-many-statements
# -*- coding: utf-8 -*-
"""Dracula color scheme for ranger."""
from __future__ import absolute_import, division, print_function

from ranger.gui.color import (
    black,
    blue,
    bold,
    cyan,
    default,
    default_colors,
    green,
    magenta,
    normal,
    red,
    reverse,
    white,
    yellow,
)
from ranger.gui.colorscheme import ColorScheme


class Dracula(ColorScheme):
    """Dracula color scheme."""

    progress_bar_color = 135

    @staticmethod
    def use(context):
        """Using the Dracula theme."""
        fg, bg, attr = default_colors

        if context.reset:
            return default_colors

        if context.in_browser:
            if context.selected:
                attr = reverse
            else:
                attr = normal
            if context.empty or context.error:
                fg = 242
                bg = 235
            if context.border:
                fg = default
            if context.media:
                if context.image:
                    fg = 211
                else:
                    fg = 141
            if context.container:
                fg = 95
            if context.directory:
                fg = 141
            elif context.executable and not any(
                (context.media, context.container, context.fifo, context.socket)
            ):
                fg = 81
                attr |= bold
            if context.socket:
                fg = 189
                attr |= bold
            if context.fifo or context.device:
                fg = 221
                attr |= bold
            if context.link:
                fg = 141 if context.good else 203
                attr |= bold
            if context.tag_marker and not context.selected:
                attr |= bold
                if fg in (red, magenta):
                    fg = white
                else:
                    fg = red
            if not context.selected and (context.cut or context.copied):
                fg = 244
                attr |= bold
            if context.main_column:
                if context.selected:
                    attr |= bold
                if context.marked:
                    attr |= bold
                    fg = 221
            if context.badinfo:
                if attr & reverse:
                    bg = magenta
                else:
                    fg = magenta

        elif context.in_titlebar:
            attr |= bold
            if context.hostname:
                fg = 242 if context.bad else 81
            elif context.directory:
                fg = 141
            elif context.tab:
                if context.good:
                    bg = 81
            elif context.link:
                fg = 141

        elif context.in_statusbar:
            if context.permissions:
                if context.good:
                    fg = 141
                elif context.bad:
                    fg = 203
            if context.marked:
                attr |= bold | reverse
                fg = 221
            if context.frozen:
                attr |= bold | reverse
                fg = 141
            if context.message:
                if context.bad:
                    attr |= bold
                    fg = 203
            if context.loaded:
                bg = Dracula.progress_bar_color
            if context.vcsinfo:
                fg = 141
                attr &= ~bold
            if context.vcscommit:
                fg = 221
                attr &= ~bold

        if context.text:
            if context.highlight:
                attr |= reverse

        if context.in_taskview:
            if context.title:
                fg = 141

            if context.selected:
                attr |= reverse

            if context.loaded:
                if context.selected:
                    bg = Dracula.progress_bar_color
                else:
                    bg = Dracula.progress_bar_color

        if context.vcsfile and not context.selected:
            attr &= ~bold
            if context.vcsconflict:
                fg = magenta
            elif context.vcsuntracked:
                fg = 203
            elif context.vcschanged:
                fg = 221
            elif context.vcsstaged:
                fg = 81
            elif context.vcssync:
                fg = 81
            elif context.vcsignored:
                fg = default

        elif context.vcsremote and not context.selected:
            attr &= ~bold
            if context.vcssync or context.vcsnone:
                fg = 81
            elif context.vcsbehind:
                fg = 221
            elif context.vcsahead:
                fg = 141
            elif context.vcsdiverged:
                fg = magenta
            elif context.vcsunknown:
                fg = 203

        return fg, bg, attr
