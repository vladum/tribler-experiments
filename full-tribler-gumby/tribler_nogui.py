import sys
import shutil
import time
import tempfile
import random
import os
import getopt
import logging.config
from subprocess import call
from traceback import print_exc
from collections import OrderedDict

# TODO: Use abs.
TRIBLERPATH = os.path.join(
    "/home",
    os.environ["USER"],
    os.environ['TRIBLERPATH']
)
sys.path += [TRIBLERPATH]
from Tribler.Core.API import *

from util.gen_files import generate_file

# We use predefined patterns and file sizes because we need to know which hashes
# to download. Peers will choose one of these. You can use util/gen_files.py to
# make more patterns. Sizes are expressed in bytes. Chuncksize was 1024.
PATTERNS = OrderedDict(sorted({
    "209715200-00" : "161b2709445830f79d71ae72acffc5b8676061a2",
    "209715200-01" : "04bce4b980f66b041084d15d1198aa54f719534b",
    "209715200-02" : "6280cd598cdd2c4d60b022f30cb9dc0a664aef82",
    "209715200-03" : "b5256892f8badd85da83833f63e99c22a2b1f2e8",
    "209715200-04" : "69b5756df844841ccbeca3017e318a3da7fbc79f",
    "209715200-05" : "e46bd426d86ed68a4e0871a4b80e29400e70351c",
    "209715200-06" : "e88612c7418cbe7a1d7c09999e88154b09c1fa9f",
    "209715200-07" : "ffc608bd527d0acfcceb42972b52651c78b93ff0",
    "209715200-08" : "94ef32751259e4e0d62c41f6295785c3a3380e5e",
    "209715200-09" : "a1aafb37f744f278ccf3055d3963c7681721d468",
    "209715200-0a" : "bfdb48c9fd985c97525d28350a25c1281dc34218",
    "209715200-0b" : "4bcd79cbf2a1186f1ce2bca26caa319177604b2e",
    "209715200-0c" : "d46d10601c998d301297dadb4acfa93a3cad6b8e",
    "209715200-0d" : "c6b053346deb1186a46caf37d1048b81365f61a5",
    "209715200-0e" : "bc65fe687827b2d8110f4d89bff4bc9398994038",
    "209715200-0f" : "42f9698672f55358f3fce1c31b4d71bb48a1281f",
    "209715200-10" : "785cf6255e4e48bf88c7aa43d839e51afababc15",
    "209715200-11" : "d64598d496fa2bd729aee407011e3f334f5d1978",
    "209715200-12" : "7e24c0be01a5efc6be79b79917d03a2f1054ad31",
    "209715200-13" : "8824487eb2abe35c13ece8975625c5154d5eb1f4",
    "209715200-14" : "9dc5e02f574759bb398f0e13f0825fe3ef8e1b4d",
    "209715200-15" : "cfcc7549beb90ae624ffb16cc286334034f0170a",
    "209715200-16" : "1ef583d7bb930e14db421dce601887a90ce64618",
    "209715200-17" : "114f32834c37282180dc235bf45252ffd22f2e92",
    "209715200-18" : "bfe1b477644a6f548f065654c433d1353d934a1b",
    "209715200-19" : "e3198b5a1be5aa5bf33b7ffe4c88b2c94d889b54",
    "209715200-1a" : "14bf30a37019e61936cc00c4f7f640a668167d27",
    "209715200-1b" : "07779f1d85bdef332b129b02d69cb31035d63088",
    "209715200-1c" : "9f6aa216912149856622fed8b5048055ea961b6b",
    "209715200-1d" : "be579101e64a46b996e95d0ba8aef3d13265bee7",
    "209715200-1e" : "0020e106aa8fe04a52875b108c193ade96957903",
    "209715200-1f" : "ea5f28500724e2618bc62e7ac26ab84c6bf60d87",
    "209715200-20" : "b5c7e67744687856cf84ac9b9ed738dbb743b0be",
    "209715200-21" : "edbfb5a2ad5437fc70689909b10b1370ffcf7485",
    "209715200-22" : "5ba4496f0c72a5e92ec17f995a772102fadf712d",
    "209715200-23" : "fea94e127473127f0d4c2ec0f1d98f6e5d97b868",
    "209715200-24" : "332ae81cfb96b248fea4f619407014e16f256359",
    "209715200-25" : "b18415f5bb5a87fe6db468c94401261e2f253cfc",
    "209715200-26" : "b812c51987be2aba467ba235f5ed4d02092ef463",
    "209715200-27" : "7c5787f021b3c0d787bac813aed6417fbc798b54",
    "209715200-28" : "9f2e103641040ce55e5a445b6d15a6ef5ba8b4f2",
    "209715200-29" : "024170f84cdaae7d8215f33d7f1d9a3360d1bc8e",
    "209715200-2a" : "f55e242e6f3f5cd71b1f68a8ac93bb6f8a569e71",
    "209715200-2b" : "e72d700b6abcd327025340667a186768228cfc9f",
    "209715200-2c" : "aaa673b607d6791323e46fb8d965e71614afeae1",
    "209715200-2d" : "4208430d21b8d58a0d955381a9929940eb915bec",
    "209715200-2e" : "57253c138ba9af092f893ff0f1f818e40799cff9",
    "209715200-2f" : "ba74ed633e3d1b272b4b58ab3273fa0b69e29edc",
    "209715200-30" : "27f8c7b59f6e0541b9895dd9273c1cd8fa556b93",
    "209715200-31" : "0d36dfb2043d80743155b03e7ccb9bd39488ba5c",
    "209715200-32" : "d7113a1610820a85b91798ca38aaf5afd5a2dbc4",
    "209715200-33" : "5479856ac2894f9acb0dff19d63062bf4e48914d",
    "209715200-34" : "c5fd855aca1c23df344db601359cf84f01d84a90",
    "209715200-35" : "23d5e390da70e493fdcf611fa1000c91bbdc1a36",
    "209715200-36" : "e8590a51a9117bd3b95d2320254d504cd135920e",
    "209715200-37" : "b8d5ce1f5457d0c4877ff005d632ce7373b47b60",
    "209715200-38" : "c51971a102590bb8b4c2e218d24e3434ec2f9d6d",
    "209715200-39" : "f40ecd688312651493fa6593450723e6bee8f7be",
    "209715200-3a" : "6bbe3c7ccaca1749f7a9a89acb47debf95a8fe3e",
    "209715200-3b" : "616eb444ae41ffab87445579ccc85c5aa7be3a55",
    "209715200-3c" : "081d9d4e57773adc9976b109495e78ec5ac12bbd",
    "209715200-3d" : "c922113086a66898eb417e341b08bfff3e54efc4",
    "209715200-3e" : "f1e3d6e86a148274c514fcc82c176444169ce662",
    "209715200-3f" : "d9bb0bd9cfa871de1d4f8edb7fc3b3ce88d43150",
    "209715200-40" : "0f4fe4dbd9c1155edd49247184e5284d5fe3d216",
    "209715200-41" : "a52f8143c0a26435be623ce682df6818e9432e28",
    "209715200-42" : "1ec600da854364266d1cc0c0c2a9605818f06a35",
    "209715200-43" : "2862b89b2033ad6704f0d314a4933c77d3b64ce6",
    "209715200-44" : "10db5ae6466c5931f7a8ba007addfec9ed9a8b5a",
    "209715200-45" : "2f476b51e6dc6cd1d787c90bcdd273f7a688d218",
    "209715200-46" : "eb5325d1916e19726978fd22501bef56cf4eac27",
    "209715200-47" : "8b5fc3ba207ab7509d62961d8a5170947e1b283d",
    "209715200-48" : "08b8919eb1aa39bd1c763a26c0189b88edd6e347",
    "209715200-49" : "e8d9787e60f88da3988689114e51089328f3a903",
    "209715200-4a" : "fef1183dccb46c4a40d44d69a85bfd4029cd2fbc",
    "209715200-4b" : "794d92c88431e17a727210a7ff8bd957d8855563",
    "209715200-4c" : "68bf38ba9398eb9f2543fecfed1bc57cb1d6ccb2",
    "209715200-4d" : "8f00c089bb76633e935034e01b2224691e530de1",
    "209715200-4e" : "5fa89a51fe455c81c3927f96757596bfd797bbd9",
    "209715200-4f" : "c4f7f59a65daebae137fa5c802e4708c178e07b1",
    "209715200-50" : "f4a42829630bb72eaffddf4c0ff647d5d0adc34f",
    "209715200-51" : "04c1e9fc93f752140d2f31a66a7d3cdde3510eda",
    "209715200-52" : "25d2c932af1fa134f7f506a3b89019bc3b53666b",
    "209715200-53" : "8c8fa3ef8001ee1bfe31d9388b8da1da59e94b72",
    "209715200-54" : "65d12f3060bb94b073344fd3c6403e8b24e8b4c5",
    "209715200-55" : "e7b88b3aec462b067607f85510cfc78069bdd774",
    "209715200-56" : "3af83e8a77aaeddf7e242a080cfc0b90d1960038",
    "209715200-57" : "38e219688f5bac71d7848af6645c82b9832edfda",
    "209715200-58" : "e3ee06bf48b49d85d9a3d2195cf159b4a46b164a",
    "209715200-59" : "f44327d6505221471494778ec74bd12efd2cd3d7",
    "209715200-5a" : "83ecf95fa051c5c4516806e2fd6878a7f93badc8",
    "209715200-5b" : "a0ee2ffce73b4a8db8913c642a41122f810d5176",
    "209715200-5c" : "b025dc18926832865ed656558ce11de1707a2cc1",
    "209715200-5d" : "8d410749c9f68c36bf6e7a70e0e5ae0745649a04",
    "209715200-5e" : "5c05d90a8acf78b63337fb5db0c0804ecf19a498",
    "209715200-5f" : "092badfc75b9cd1ce62ff9380af49479654add1b",
    "209715200-60" : "321ab7cf361f2b1145794dfef7242b75239ac0f3",
    "209715200-61" : "b9d2effb6511ba0b2098eb5f76447e22421d2ed9",
    "209715200-62" : "0a0efb8275602f31ded4645519107fbf0105b436",
    "209715200-63" : "02eee994dc457908ea9b8932d36f47c15f21053b",
    "209715200-64" : "7354ce7aaa1d8768978100d03bd3262a6f21d2f7",
    "209715200-65" : "d13569d057be533fbbfc068fc3134f56fc9ebed9",
    "209715200-66" : "6f55eab18e35579df23f20ae6c7a5ac9b1cf13b1",
    "209715200-67" : "9aa0bb1b2bf8bd59d1264ec13641c22f034b462c",
    "209715200-68" : "b036f612ac6ef8f9f8818ee7f69179574c66bfb4",
    "209715200-69" : "926ad07617246088ea19edfc328c26d07b19af6c",
    "209715200-6a" : "50cde0d2db3af573c7d2416fc2bfb15e1b06a62e",
    "209715200-6b" : "84b885f13474b93db26b7816ed47933584b1f1af",
    "209715200-6c" : "2e1c7d731252fb7590c42621fdf186003926c160",
    "209715200-6d" : "89ee92a4c95a891378953b8d547064dbefbf9a15",
    "209715200-6e" : "8d84c1930a5a4899c49342980dae2cfd2f28677c",
    "209715200-6f" : "68d3f1785a69b8b6c295f6e16f3cf1ae72605910",
    "209715200-70" : "daf5302278fc4b991d90f2d50cfff5a8deab2a60",
    "209715200-71" : "300658509592c0f57ee17e2b6f11fba8d770dfa9",
    "209715200-72" : "f5fa44768abc38b695caf663ff54ff7c9559f057",
    "209715200-73" : "7bb0c965447f8f7b8f10ce2f3dae6fc0bffa33d1",
    "209715200-74" : "ba512c17b733fec1687ae0a6f6ee996a565a029c",
    "209715200-75" : "b52764b67d0f2cfaf65c1305d2ec63bb741bd748",
    "209715200-76" : "d026a9bf512a7b1a06486a8735412b9c319f7398",
    "209715200-77" : "cad374437ba72d24216d225fa5fdd184b74396b5",
    "209715200-78" : "71d5d5be66f1d6c559aeef23fab89274ea780341",
    "209715200-79" : "d3f85b608eac75b83ee522a2ad25d39249079747",
    "209715200-7a" : "282a7edd302927c6f117e110115742173288d053",
    "209715200-7b" : "c47f4a064e506e1a1728a8fa17b6d853f28c1ae1",
    "209715200-7c" : "8ea74b3dac8c826e5acab28c7879480e6a7018d2",
    "209715200-7d" : "1f38d58c7c73a527449ff760cd35cb91089c6a45",
    "209715200-7e" : "bcaafa047dc678b02239a9ee61d125e0cb58d9b9",
    "209715200-7f" : "7932301ba11d42eb8a23873627a0942057791d69",
    "209715200-80" : "df6eeefa54ec73bd2b1d16fcd8f2deefe1fed33d",
    "209715200-81" : "e9818dfdcf4cc2ef31fabfb608563458a52f32a3",
    "209715200-82" : "0635e32e9efb03764b4797997e00f0641cd4bd13",
    "209715200-83" : "0648f3dc579bf17dda06b3669f0678c0bd571365",
    "209715200-84" : "8b0e549763554f5b650a109bd9999e641a9736c6",
    "209715200-85" : "f955f3f8ada710ccc76b681e733c2014a334910c",
    "209715200-86" : "8b4a0967fe1c06a70686fb53ad3e871dc6d8e072",
    "209715200-87" : "09ab6f25ea08282676cdc27efa5a6c0658521ba6",
    "209715200-88" : "78ee414be0d5d0afe12b360b3339e0c06144c463",
    "209715200-89" : "7b2264549356a070fbc629d7b49226576cc7a3b3",
    "209715200-8a" : "d0872cc2a432ba64ef7369ac298fa449545f6d6f",
    "209715200-8b" : "88cd1dcafccc5ecf45469b95d511a0922a8bda8e",
    "209715200-8c" : "bad22ad90a10dc0114c43d5990c71565533e2e4a",
    "209715200-8d" : "299c8d677fae72e07210226fa93dd979a705fa17",
    "209715200-8e" : "9f64cf51cece532c6c59d2a5c00bace2b1daf4c9",
    "209715200-8f" : "d53cec97dd0640bfa8490408de153b7616c63dec",
    "209715200-90" : "db49f5ea4bc44f895563194c822bfa50af2be3d9",
    "209715200-91" : "d72333717108ade3244c8e7bcf2fc32f718d8dae",
    "209715200-92" : "12befa0122eb5c3c0f086e335aea4444f51046d0",
    "209715200-93" : "02ba8105b5b017ee14ad4bce499860d0a56cf01d",
    "209715200-94" : "4e64597bfb0d6848952a554704b42fa607d81df7",
    "209715200-95" : "11b10a62d16f45d442be3dc31eaa888360d87588",
    "209715200-96" : "3b10f6db3fd8bd38c37e57a4fdaa96bd1c5515e5",
    "209715200-97" : "d2f2e03de7e786366500b4ffdfdd3b1d62827277",
    "209715200-98" : "247703440506b8ffe4a5390cc94bf87c1d679c67",
    "209715200-99" : "e9205f3e1224a366138f972a38b4b4581a51b0a2",
    "209715200-9a" : "ebbe1e683fa61f51d618c82d10f66adbbe896fc9",
    "209715200-9b" : "0d46006a0c194efdff8e6f4481c621601c0a40fc",
    "209715200-9c" : "fbaaa3424ff574fc1b57f9bb2e80cf62ef92d26c",
    "209715200-9d" : "a703289fa5ec93a43f7c2beec89992271c268750",
    "209715200-9e" : "67851e54f87bf96dc26ab0feb9dc7d3d0c25d0af",
    "209715200-9f" : "86a14fd3500fecfa4aa15b2a319fa0b13a408900",
    "209715200-a0" : "480933cd2fef59129b2cbfc970218048f9483bd8",
    "209715200-a1" : "29ac9f6be6c611555c253314d0725856971ea09d",
    "209715200-a2" : "0deafec42e2fcb2de1f957aca6e3f3e2d4c89496",
    "209715200-a3" : "7c565daf396fe082fc46eea8f80ca264ad470f42",
    "209715200-a4" : "9dd3230bc53abdf6ed0c5f380e778c6d693d528b",
    "209715200-a5" : "2a884ce43be51e4dfac7b6f8ea236389fe8a1286",
    "209715200-a6" : "d3a8e8ddbbbb18a0bb5874c4d0ccecb5773e54c6",
    "209715200-a7" : "8c6c58f41c69121b66a69d9165dfc5b44b8ab642",
    "209715200-a8" : "27fe6299582ece5b855918cf5e1e2fe5383f46ea",
    "209715200-a9" : "946cc1e4139587a591dfe0b9f0c0093e97d73e37",
    "209715200-aa" : "9d82c58c9abeea2d6aeb75ecd1fee309c669d76a",
    "209715200-ab" : "fb0d8221c952c12d04db26f16a34dd085442f11f",
    "209715200-ac" : "d20767735efec5db22b7dbe60e9cfaeecd12b04f",
    "209715200-ad" : "6e754a7408c8fd12fabbe60ccbb5415d3c8d5aa0",
    "209715200-ae" : "8d2c63e5e4fd1495f30a0cf9558685daa21cf436",
    "209715200-af" : "8a38c95ac06e0a99ddbed99d121bdb9f7a35400d",
    "209715200-b0" : "7810ff558dbf8134e2e4935182d604c83ed9efb0",
    "209715200-b1" : "4417fbc52482badedf131484348ebd1324f13d0f",
    "209715200-b2" : "469f0daaae8275c01409fe61b942b7f5c7ccc651",
    "209715200-b3" : "48e2a09bf7be08f0b9d70503ee225dafbeee29ef",
    "209715200-b4" : "b2466747b74333f80843919e613c9dfc35877afd",
    "209715200-b5" : "02b3cfcc798757de527bd203c378c9b461d81178",
    "209715200-b6" : "93190de6fcc2ced02723a812622f984a1ee4c8fe",
    "209715200-b7" : "efb5c1da264f67254f5fc16db408a668ebfc51b0",
    "209715200-b8" : "1d3769ba6ebad2931e8b0610d013a9fe4e59fbce",
    "209715200-b9" : "16993bf21b96e6514f0e544fa03b3597fadc344e",
    "209715200-ba" : "8d37a3586fc474e4628a3e80c6d6521af18a5625",
    "209715200-bb" : "23008585886cb2b70798e436cc55dac9df9935a7",
    "209715200-bc" : "e7f4d3c5e27cd6ca26a0d9a020ec44a8f4939f71",
    "209715200-bd" : "96dbaca57a96d8e33fff04d6d0d8ebc96ca5bf96",
    "209715200-be" : "45da3a783d3fc62cf15211e325a5255b7a21053b",
    "209715200-bf" : "0a136397697994acd1981ef3523fcf086d8c083f",
    "209715200-c0" : "16af5997cef014832869cf164d4fdff65a906f15",
    "209715200-c1" : "375678837986bcc4a99d429e88f1e55514e8e5f9",
    "209715200-c2" : "476da2148bd464000a58b24b794edacc1117c42d",
    "209715200-c3" : "63cdd08faacd2149e841801a32009507b0636a71",
    "209715200-c4" : "8a7361c737d0cf3f4f69bc577a27f94c40d06c3f",
    "209715200-c5" : "afc42fc48f5dd149e2f8b9ff5f55ccbfc0470fdd",
    "209715200-c6" : "40b6c917de8025281ffd0acceb06aaa458cce796",
    "209715200-c7" : "87bad1676a9edbe89e1a593a583fcb5bdc21e37a",
    "209715200-c8" : "26e013ddfe0e283ade8159e64c0afe84bd605686",
    "209715200-c9" : "5e36bd4ba3b48b779c3caac76981a4662b9336e8",
    "209715200-ca" : "729c05850d7971d3794773e3043a5788dd8540bf",
    "209715200-cb" : "4695f6d16df8febf60dbb86997ad52d3a3698d6e",
    "209715200-cc" : "cd248ea820bfd64bbb215576c281669503704392",
    "209715200-cd" : "5ec42498c42b90f48cc78482df7c28dfcd2483c5",
    "209715200-ce" : "32d8eff939a0df137c73b2b49f768e8a47ded948",
    "209715200-cf" : "9006543216de9eb73c948815afb90265ee01e1d1",
    "209715200-d0" : "8ae106de3aa9c477a88df59a19afe1e1adca9755",
    "209715200-d1" : "a883ba0bc2d5015dc2269ac0b45d646205f014ab",
    "209715200-d2" : "fbe42e2f2ec89b5396957bf7f633caab81b195ea",
    "209715200-d3" : "e931bb769f5e3680182036692cf5469064a34ea7",
    "209715200-d4" : "d857d020a2d3c36db56d0f562c8ebabed4075029",
    "209715200-d5" : "dcc2568df3481863f8b1a369903b2b82315b8904",
    "209715200-d6" : "87b00c2fa7bd938d645fa8e5f8f4efb55da40f5b",
    "209715200-d7" : "15182463f7261960411950dd68cd2d0222e76c1f",
    "209715200-d8" : "9cc52c7d3d7116718b1fda3afa3605a30ff4aaee",
    "209715200-d9" : "28b058d381f484483bb940c7700bb03945c5cceb",
    "209715200-da" : "4b4113d06c9158cd759e1c0e854cd3263cbf24e0",
    "209715200-db" : "559b36ccefa38d3ae5ad8de7ff3e78c83f70ae22",
    "209715200-dc" : "1ee063e442d00fefbe7922b8d24dfd9d5c397406",
    "209715200-dd" : "e76c4f8f411a91bfe335245bcc6a5abc3c65ef50",
    "209715200-de" : "71c987becdbb99cdd97613983bdd52f58535e682",
    "209715200-df" : "fc051a0a86c298480d6242bca58c790be73768f5",
    "209715200-e0" : "954ec08aa3472e1477a47ba6ec1b6c672858b3c1",
    "209715200-e1" : "459c54d17ff7e3a0cf3ae5eb7afde685bba724a2",
    "209715200-e2" : "83c5ba1e8d5dbf344dda5b4dcbd132e4651d24d1",
    "209715200-e3" : "d8998278afb3f30098f53e25be1d64f6ca585bed",
    "209715200-e4" : "98e2393059112388754fbe38b717df0c850d6a7b",
    "209715200-e5" : "60ed5320c9f8765a65a23328658f4769115bb383",
    "209715200-e6" : "e513a705e46f5314104c5452e369434e79e3fad2",
    "209715200-e7" : "4519e946c736e6ad0b29336e35dd3d8a36042356",
    "209715200-e8" : "7310f40f891a0f360ced94ba779f11cc47ce8ef2",
    "209715200-e9" : "af87404049ffe7188be7f49e2d3a0e6a4d66a068",
    "209715200-ea" : "55e9c226359eaf17933cb9a6ba61e505bf4a518d",
    "209715200-eb" : "be25add59d664920c9b2758ef4d418bd55d73d75",
    "209715200-ec" : "40b7fc32ca457e65e0b4aea58db96e7810256024",
    "209715200-ed" : "43097ff8828749ff9935363075fdb7cc6bf37a17",
    "209715200-ee" : "7688b1e4515fe364a65ebf5c96ef7d619c65e1a2",
    "209715200-ef" : "df08211579912c607fbc2ea4f47e5b14540dfbb3",
    "209715200-f0" : "c0fe42e7829c73a083b4a31efd86513b3ef28c74",
    "209715200-f1" : "260faeb4bdaf62d42f0d56af60a4b849eccf3cb5",
    "209715200-f2" : "eb30c9ed1b1adca52730abc3ff32dc207a015014",
    "209715200-f3" : "c365cb024b1671d92e06dfa1b080dbfe29061fec",
    "209715200-f4" : "53493c61088d9ad037313020a90a5b0a04659a99",
    "209715200-f5" : "bd1f22d847cb873a94c432351a232057b6447afc",
    "209715200-f6" : "495db801b16c2078c46e457a1f2e25e680bae679",
    "209715200-f7" : "601b28b50d7f5b6196d1fe9a537d2cc095f52546",
    "209715200-f8" : "b8b0044d8d60313aff8c412fbb9d891a74de0eaf",
    "209715200-f9" : "128afe607f588cc1fecdc6be62f1f5d6bf25d6c3",
    "209715200-fa" : "bb04c94ac118e05699963d253cdfec4ce5a74034",
    "209715200-fb" : "14bbc9b7b1f7d4c96521e054bf2797c86e4b9a0b",
    "209715200-fc" : "c8d8400432240e2df5c7394e4dcb9ebfaa1c61f6",
    "209715200-fd" : "7ecb98892f0cd61d63ad221baea90056cda377af",
    "209715200-fe" : "a3f87613c51bf67aa56229fef73782daeb5db921",
    "209715200-ff" : "c0c50c6c588f082b665b64c56ae7a6a53798a91d"
}.items()))

def download_state_callback(peerid, ds):
    """
    Logs download progress while the experiment if running.
    """
    d = ds.get_download()
    print >> sys.stderr, '%s %s %s %5.2f%% %s up %8.2fKB/s down %8.2fKB/s' % \
        (peerid,
        d.get_def().get_name(),
        dlstatus_strings[ds.get_status()],
        ds.get_progress() * 100,
        ds.get_error(),
        ds.get_current_speed(UPLOAD),
        ds.get_current_speed(DOWNLOAD))

    return (1.0, False)

class TriblerNoGui:
    """
    This only runs Tribler's Session. No GUI, no wx stuff. It also defines
    methods that will be called while the experiment's scenario unfolds.

    Available scenario actions:
        * generate_file
        * seed
        * leech
    """
    def __init__(self, id, swiftport, rootdir, config=None):
        """
        This only prepares the SessionStartupConfig object. Call start() to
        actually start Tribler.
        """
        self.config = config

        self.rootdir = rootdir
        if not os.path.exists(self.rootdir):
            os.makedirs(self.rootdir)
        os.chdir(rootdir)

        self.peerid = id
        self.filesdir = os.path.join(self.rootdir, 'files' + self.peerid)
        os.makedirs(self.filesdir)
        self.statedir = os.path.join(self.rootdir, 'state' + self.peerid)

        self.sscfg = SessionStartupConfig()
        self.sscfg.set_state_dir(self.statedir)
        self.sscfg.set_swift_path(
            os.path.join(TRIBLERPATH, 'Tribler', 'SwiftEngine', 'swift')
        )
        self.sscfg.set_swift_tunnel_listen_port(swiftport)
        self.sscfg.set_dispersy_tunnel_over_swift(True)

        # we only play with swift and dispersy in this experiment
        self.sscfg.set_swift_proc(True)
        self.sscfg.set_dispersy(True)

        self.sscfg.set_libtorrent(False)
        self.sscfg.set_megacache(False)
        self.sscfg.set_torrent_collecting(False)
        self.sscfg.set_mainline_dht(False)

    def _get_peer_endpoint(self, peerid):
        endpoint = self.config["others"][int(peerid) - 1]
        return "%s:%s" % (endpoint["ip"], endpoint["port"])

    def start(self):
        self.s = Session(self.sscfg)
        self.s.start()

        # load Dispersy BarterCommunity
        def define_barter_community():
            from Tribler.community.bartercast3.community import BarterCommunity

            if swift_process:
                dispersy.define_auto_load(BarterCommunity,
                                          (swift_process,),
                                          load=True)

            print >> sys.stderr, "tribler: Dispersy BarterCommunity is ready"

        swift_process = self.s.get_swift_proc() and self.s.get_swift_process()
        dispersy = self.s.get_dispersy_instance()
        dispersy.callback.call(define_barter_community)

    def shutdown(self):
        self.s.shutdown()
        time.sleep(3)
        shutil.rmtree(self.statedir)

    def generate_file(self):
        (sizepattern, roothash) = PATTERNS.items()[int(self.peerid)]
        size, pattern = sizepattern.split("-")
        filename = os.path.join(self.filesdir, "file_" + roothash)
        generate_file(
            int(size),
            pattern.decode("hex"),
            filename
        )
        logging.info(
            "Peer %s generated file: hash=%s size=%s pattern=%s name=%s" % 
            (self.peerid, roothash, size, pattern, filename)
        )

    def seed(self, filename):
        sdef = SwiftDef()
        # using the torrent collection swift instance (not the 9999 port one)
        sdef.set_tracker(self._get_peer_endpoint(self.peerid))
        sdef.add_content(os.path.abspath(os.path.join(self.filesdir, filename)))
        sdef.finalize(self.s.get_swift_path(), destdir=self.filesdir)

        dscfg = DownloadStartupConfig()
        dscfg.set_dest_dir(os.path.join(self.filesdir, filename))
        dscfg.set_swift_meta_dir(self.filesdir)
        

        d = self.s.start_download(sdef, dscfg)
        dsc = lambda x: download_state_callback(self.peerid, x)
        d.set_state_callback(dsc, getpeerlist=[])

    def leech(self, peerid, roothash):
        url = 'tswift://%s/%s' % (self._get_peer_endpoint(peerid), roothash)
        sdef = SwiftDef.load_from_url(url)

        dscfg = DownloadStartupConfig()
        dwload_dir = os.path.join(self.rootdir, 'dwload' + self.peerid)
        dscfg.set_dest_dir(dwload_dir)
        dscfg.set_swift_meta_dir(dwload_dir)

        d = self.s.start_download(sdef, dscfg)
        dsc = lambda x: download_state_callback(self.peerid, x)
        d.set_state_callback(dsc, getpeerlist=[])

    def test_method(self, param="bau"):
        print "Test method called at", time.time(), "by peer", self.peerid,\
              "with param", param
