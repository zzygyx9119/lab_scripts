import argparse
import re
import math

"""
Input:
Requires filepath to a segmentation file. This segmentation file will be converted to IGV format. Additionally, the user is able to specify whether the segmentation file is generated by 'sequenza' or 'titan' using the '--mode' parameter. If 'sequenza' is specified in the '--mode' parameter, the '--sequenza_sample' parameter must also be set. The '--sequenza_sample' parameter specifies the sample name for the 'sequenza' segmentation file. Alternatively, if the segmentation file is neither 'sequenza' or 'titan', then the user must specify the column indices (1-based numbering) for the sample name ('--sample_col'), chromosome ('--chrm_col'), start position ('--start_col'), end position ('--end_col') in the segmentation file. The user must also specify the column indices (1-based numbering) of either the log ratio column ('--log_r_col') or the depth ratio column ('--d_ratio_col') in the segmentation file. 

Output:
Outputs a '.seg' file that is in IGV format.
"""


def main():
    args = parse_args()

    check_arguments(args)

    args = add_to_MODES(args)

    header_checked = False

    mode = args.mode

    for seg in seg_file:

        if not header_checked:
            p = re.compile('start', re.I)
            m = re.search(p, seg)

            header_checked = True

            if m:
                continue

        fields = seg.split('\t')

        vals = [ fields[MODES[mode]['chrm_col']], fields[MODES[mode]['start_col']],
                 fields[MODES[mode]['end_col']] ]

        if mode == 'sequenza':
            vals = [ args.sequenza_sample ] + vals

        elif mode == 'titan' or mode == 'other':
            vals = [ fields[ MODES[ mode  ][ 'sample_col' ] ] ] + vals

        if 'd_ratio_col' in MODES[mode]:
            log_ratio = math.log(float(fields[MODES[mode]['d_ratio_col']]),2)
            vals = vals + [ log_ratio ]

        elif 'log_r_col' in MODES[mode]:
            vals = vals + [ fields[ MODES[mode]['log_r_col'] ] ]

        print '{}\t{}\t{}\t{}\t{}\t{}'.format(*vals)

    return


def add_to_MODES(args):
    mode = args.mode

    if mode not in MODES.keys():
        mode = 'other'
        args.mode = mode
        MODES[mode] = {}

        MODES[mode]['sample_col'] = args.sample_col - 1
        MODES[mode]['chrm_col'] = args.chrm_col - 1
        MODES[mode]['start_col'] = args.start_col - 1
        MODES[mode]['end_col'] = args.end_col - 1

        if args.log_r_col:
            MODES[mode]['log_r_col'] = args.log_r_col - 1
        elif args.d_ratio_col:
            MODES[mode]['d_ratio_col'] = args.d_ratio_col - 1

    return args


def check_arguments(args):

    if args.mode == 'sequenza' and not args.sequenza_sample:
        raise ValueError("Must specify '--sequenza_sample' when '--mode' is set to 'sequenza'.")

    if not mode:
        if not all(args.sample_col, args.chrm_col, args.start_col, args.end_col) and not any(args.log_r_col, args.d_ratio_col):
            raise ValueError("Specify '--sample_col', '--chrm_col', '--start_col', '--end_col'. Also specify either '--log_r_col' or '--d_ratio_col'.")

        if args.log_r_col and args.d_ratio_col:
            raise ValueError("Cannot specify both '--log_r_col' and '--d_ratio_col'.")

    return


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('seg_file', type=argparse.FileType('r'),
                        help='Segmentation file to convert to IGV format.')
    parser.add_argument('--mode', choices=MODES.keys,
                        help='Indiciate whether segmentation file is Sequenza or TITAN.')
    parser.add_argument('--sequenza_sample',
                        help='Specify sample name for Sequenza segmentation file.')
    parser.add_argument('--sample_col', type=int,
                        help='1-based index of sample name column in segmentation file.')
    parser.add_argument('--chrm_col', type=int,
                        help='1-based index of chromosome column in segmentation file.')
    parser.add_argument('--start_col', type=int,
                        help='1-based index of segment start position column in segmentation file.')
    parser.add_argument('--end_col', type=int,
                        help='1-based index of segment end position column in segmentation file.')
    parser.add_argument('--log_r_col', type=int,
                        help='1-based index of log ratio column in segmentation file.')
    parser.add_argument('--d_ratio_col', type=int,
                        help='1-based index of depth ratio column in segmentation file.')

    args = parser.parse_args()

    return args

MODES = {
          'titan' : 
                    {
                      sample_col: 0,
                      chrm_col: 1,
                      start_col: 2,
                      end_col: 3,
                      log_r_col: 6 # Log Ratio
                     },
          'sequenza' :
                       {
                         chrm_col: 0,
                         start_col: 1,
                         end_col: 2,
                         d_ratio_col: 6 # Depth Ratio
                        }
        }

if __name__ == '__main__':
    main()