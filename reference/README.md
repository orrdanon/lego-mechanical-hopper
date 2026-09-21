# reference/

Third-party source models, stored **unmodified** and never written or
imported by the project.

## `htd3m_40t_40015040.stp` -- not yet added

CADENAS PARTsolutions model 40015040: a 40-tooth HTD-3M pulley for 15 mm
belt. Licence per the file's own header: CC BY-ND 4.0, credit CADENAS. "No
derivatives" is why it must be committed exactly as downloaded.

Only its groove is used. The five `PULLEY_GROOVE_*` values in `params.py`
and the four `FILE_JUNCTIONS` points in `tests/test_profile.py` and
`checks.py` were read from this file's B-rep (drivetrain-spec §3.3, §4.4);
`profile.py` rebuilds the groove from those values and is tested against
those points. Its flanges, 6 mm pilot bore, 19 mm face and hub are
irrelevant.

The file was not available when the drivetrain was implemented, so
drivetrain-spec §14 item 5 is open until it is dropped in here under
exactly that name.
