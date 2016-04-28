# tamnon v0.1
These are the files for running tamnon, a dialect analyzer for Ancient Greek.
For now, it does binary differentiation between Attic and Doric forms.

## Running tamnon

Save the input data as a [textname].txt file in the "texts" folder (the full
text of Pindar's work, from the Perseus Digital Library, has been included).

Then, run
`python2 tamnon_preprocess.py [textname]` (this may take a few minutes)

This will create a set of intermediate files in the "intermediate files" folder.

Next, run `python2 tamnon_process.py [textname]` (this may also take a minute or two, but less than the preprocess)

which will create a variety of result files, stored in results/[textname]/

The result files are as follows:

- overall.txt contains an overview of the results, without individual tokens.
- dialect.txt contains the number of forms and tokens for each dialect.
- rules.txt contains the number of forms and matching tokens for each rule.
- tokens.txt contains the list of every token (in text order) with its parses.
- evaluation.txt contains comparisons between Morpheus' dialect analyses and
    tamnon's dialect analyses.
- all.txt contains all information combined in a single file.
- the graphs folder contains the rules results in graph form.
----
## GUI Form
Alternatively, you can run `python2 tamnon_gui.py`
to open a small graphical user interface that allows instant feedback on text
placed into the upper textarea.

If you only want to examine portions from a text you have already preprocessed,
you can run `python2 tamnon_gui.py [textname]`
to avoid rerunning the morphological parses each time.

--------

## Testing
To test the tamnon rules, run
"python2 tamnon_get_test_forms.py"
every time you change the forms that are to be tested on,
then run
"python2 tamnon_test_rules.py"
to test all of the rules and ensure they are working. Any errors will
appear under the header of the appropriate rule.

----

License
----

MIT
