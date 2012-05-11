# -*- coding: utf-8 -*-
"""
---------------------------
volt.plugin.builtins.atomic
---------------------------

Atom feed generator plugin.

:copyright: (c) 2012 Wibowo Arindrarto <bow@bow.web.id>
:license: BSD

"""

from __future__ import with_statement
import os
import sys
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from volt.config import CONFIG, Config
from volt.plugin.core import Plugin


class AtomicPlugin(Plugin):

    """Creates atom feed of engine units.

    This plugin generates atom feed from the units of its target engine.
    The processed units must have a datetime header field.

    Options for this plugin configurable via voltconf.py are:

        `FEEDS`
            Dictionary that determines what feeds to create.

        `OUTPUT_DIR`
            Name of the directory for the output file, defaults to 'site'.

        `TEMPLATE_FILE`
            Name of the template atom file.

        `TIME_FIELD`
            Name of the unit field containing the datetime object used for
            timestamping the feed items.

        `EXCERPT_LENGTH`
            Character length of the excerpt to show in each feed item.

    """

    DEFAULTS = Config(
        # feeds to create
        # dictionary of unit attributes as keys
        # and output filename as values
        # if the key is an empty string (''), then all engine units are used
        FEEDS = {
            '': 'atom.xml',
        },
        # output directory name
        OUTPUT_DIR = CONFIG.VOLT.SITE_DIR,
        # jinja2 template file, try CONFIG.VOLT.TEMPLATE_DIR first
        # then use builtin directory.
        TEMPLATE_FILE = 'atom_template.xml',
        # unit field containing datetime object
        TIME_FIELD = 'time',
        # excerpt length in feed items
        EXCERPT_LENGTH = 400,
        # how many items in a feed
        FEED_NUM = 10,
    )

    USER_CONF_ENTRY = 'PLUGIN_ATOMIC'

    def run(self, engine):
        """Process the given engine."""

        # jinja2 Env: Load custom template first, falling back to the builtin
        env = Environment(loader=FileSystemLoader(
                [CONFIG.VOLT.TEMPLATE_DIR, os.path.dirname(__file__)]))
        # pass in a built-in Volt jinja2 filter to display date
        env.filters['displaytime'] = CONFIG.SITE.TEMPLATE_ENV.filters['displaytime']
        template = env.get_template(self.config.TEMPLATE_FILE)

        # render and write to output file for each key: value pair in FEEDS
        for field, outfile in self.config.FEEDS.iteritems():

            atom_file_ptr = os.path.join(self.config.OUTPUT_DIR, outfile)

            # if attr == '', then we take all units
            if field == '':
                units = engine.units
                self.write_feed(units[:self.config.FEED_NUM], atom_file_ptr, template)
            # otherwise check the value type and write its corresponding feed
            else:
                # sample to determine value type, and how to extract
                # field values afterwards
                sentinel = getattr(units[0], field)

                # we can handle value extraction if the value type is list / tuple
                if isinstance(sentinel, (list, tuple)):
                    item_list_per_unit = (getattr(x, field) for x in units)
                    field_values = reduce(set.union, [set(x) for x in item_list_per_unit])
                # or if it's an str / int / float
                elif isinstance(sentinel, (str, int, float)):
                    field_values = set([getattr(x, field) for x in units])
                # but not anything else
                else:
                    raise NotImplementedError("Atomic could not process the "
                            "type %s." % sentinel.__class__.name)

                for value in field_values:
                    units = [x for x in engine.units if value in getattr(x, field)]
                    atom_file = atom_file_ptr % str(value)
                    self.write_feed(units[:self.config.FEED_NUM], atom_file, template)

    def write_feed(self, units, outfile, template):
        """Writes a feed output file.

        units -- List of units to write in the feed.
        outfile -- String of output feed filename.
        template -- Jinja2 template object used to render the output.

        """
        # set feed generation time
        time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        rendered = template.render(units=units, CONFIG=CONFIG, time=time)
        with open(outfile, 'w') as target:
            if sys.version_info[0] < 3:
                rendered = rendered.encode('utf-8')
            target.write(rendered)
