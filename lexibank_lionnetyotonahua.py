from pathlib import Path
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank import Language, FormSpec, Concept, Lexeme
from pylexibank import progressbar

from clldutils.misc import slug
import attr
import lingpy


REMAP = {
        "Ma": "MA",
        "VA": "Va",
        "VB": "Vb",
        }

@attr.s
class CustomLanguage(Language):
    Abbreviation = attr.ib(default=None)


@attr.s
class CustomConcept(Concept):
    Number = attr.ib(default=None)
    Spanish_Gloss = attr.ib(default=None)


@attr.s
class CustomLexeme(Lexeme):
    ConceptInSource = attr.ib(default=None)
    Entry = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "lionnetyotonahua"
    language_class = CustomLanguage
    concept_class = CustomConcept
    lexeme_class = CustomLexeme
    form_spec = FormSpec(
        missing_data=("---",),
        separators="/;",
        replacements=[
            (" ", "_"), ('\u0306', ''), ('\u0329', ''), ('\u0303', ''),
            ('\u0325', ''), ('\u0335', ''), ('\u0331', '')],
        first_form_only=True,
    )

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """
        concepts = {}
        for concept in self.conceptlists[0].concepts.values():
            cid = '{0}_{1}'.format(concept.number, slug(concept.gloss))
            args.writer.add_concept(
                ID=cid,
                Name=concept.gloss,
                Spanish_Gloss=concept.attributes["spanish"],
                Concepticon_ID=concept.concepticon_id,
                Concepticon_Gloss=concept.concepticon_gloss,
                Number=concept.number
            )
            concepts[concept.attributes["spanish"]] = cid

        # TODO: Fix largo -> larpo
        concepts = {"larpo" if k == "largo" else k: v for k, v in concepts.items()}

        args.log.info('[i] added concepts')
        languages = args.writer.add_languages(lookup_factory="Abbreviation")
        args.log.info('[i] added languages')
        args.writer.add_sources()
        
        wl = lingpy.Wordlist(str(self.raw_dir.joinpath("yotonahua.tsv")))
        for idx in progressbar(wl, desc="forms to cldf"):
            if wl[idx, "doculect"] not in [
                    "On", "PM", "T", "V", "E", 
                    #"Es", "PI", "Tn", "Ts", "P"
                    ]:
                lex = args.writer.add_form(
                        Language_ID=languages[REMAP.get(wl[idx, "doculect"], wl[idx, "doculect"])],
                        Parameter_ID=concepts[wl[idx, "concept"]],
                        Value=wl[idx, "value"],
                        Form=wl[idx, "form"].replace(" ", "_").strip("."),
                        Entry=wl[idx, "entry"],
                        Source="Lionnet1985",
                        Cognacy=wl[idx, "cog"],
                        ConceptInSource=wl[idx, "concept_in_source"]
                        )
                args.writer.add_cognate(
                        lex,
                        Cognateset_ID=wl[idx, "cog"],
                        Source="Lionnet1985"
                        )


