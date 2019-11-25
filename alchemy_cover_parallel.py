import sh
from absl import app
from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_string("infile", None, "CSV to read ingredient data from")
flags.DEFINE_string(
    "outfile_base",
    None,
    "CSV to write potions to, with {} somewhere to distinguish results",
)

flags.DEFINE_integer("count", 10, "Number of runs to do")


def main(args):
    del args  # unused

    for line in sh.parallel(
        sh.seq(1, FLAGS.count),
        "pipenv",
        "run",
        "python",
        "alchemy_cover.py",
        "--infile=" + FLAGS.infile,
        "--outfile=" + FLAGS.outfile_base,
        _iter=True,
    ):
        print(line)


if __name__ == "__main__":
    flags.mark_flag_as_required("infile")
    flags.mark_flag_as_required("outfile_base")
    app.run(main)
