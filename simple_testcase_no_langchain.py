"""
LOB issue simple test case
"""

import oracledb
import array

from config_private import CONNECT_ARGS

#
# Main
#
print("")
print("Starting test...")

questions = ["What are the knwon side effects of metformin?,"]

#
# setup
#
# this is the embedding vector corresponding to the question

embedding_vet = [
    -0.0239105224609375,
    0.007965087890625,
    0.04669189453125,
    -0.0283966064453125,
    -0.03570556640625,
    -0.0162200927734375,
    -0.02227783203125,
    -0.0394287109375,
    -0.025360107421875,
    0.052947998046875,
    0.03973388671875,
    -0.00707244873046875,
    0.0380859375,
    -0.033966064453125,
    0.06390380859375,
    -0.006450653076171875,
    0.035308837890625,
    0.048980712890625,
    0.06756591796875,
    -0.01403045654296875,
    -0.0160064697265625,
    0.0078125,
    0.04547119140625,
    -0.021240234375,
    0.009124755859375,
    0.057586669921875,
    0.0640869140625,
    -0.047607421875,
    0.048431396484375,
    -0.00024437904357910156,
    -0.022003173828125,
    -0.03375244140625,
    0.08050537109375,
    0.01416015625,
    -0.0206298828125,
    -0.031280517578125,
    0.00811004638671875,
    -0.02294921875,
    0.01390838623046875,
    0.0133514404296875,
    -0.0212554931640625,
    -0.000988006591796875,
    -0.03924560546875,
    0.04168701171875,
    -0.0116424560546875,
    0.01483917236328125,
    0.0087890625,
    0.03472900390625,
    0.013519287109375,
    0.05279541015625,
    -0.0340576171875,
    -0.0023555755615234375,
    0.0279998779296875,
    -0.0079193115234375,
    0.0237579345703125,
    -0.010040283203125,
    -0.003265380859375,
    0.01136016845703125,
    0.02923583984375,
    0.01522064208984375,
    0.006988525390625,
    -0.008941650390625,
    -0.043121337890625,
    0.00952911376953125,
    0.025482177734375,
    0.02899169921875,
    0.002094268798828125,
    0.0189056396484375,
    -0.0178680419921875,
    -0.001743316650390625,
    0.0173492431640625,
    -0.0049285888671875,
    -0.01425933837890625,
    0.00382232666015625,
    -0.034515380859375,
    0.00848388671875,
    0.00724029541015625,
    -0.026641845703125,
    0.0256805419921875,
    0.0290069580078125,
    -0.0240478515625,
    0.00832366943359375,
    0.00212860107421875,
    0.013946533203125,
    0.013214111328125,
    -0.00789642333984375,
    -0.028472900390625,
    0.0108184814453125,
    -0.01320648193359375,
    -0.0305328369140625,
    0.05242919921875,
    0.0565185546875,
    -0.0034427642822265625,
    -0.048004150390625,
    -0.00408172607421875,
    -0.02386474609375,
    0.0654296875,
    -0.0338134765625,
    0.0175628662109375,
    0.00762939453125,
    0.00032448768615722656,
    0.006488800048828125,
    0.038421630859375,
    -0.021331787109375,
    0.02557373046875,
    -0.01544189453125,
    0.0310516357421875,
    0.002704620361328125,
    -0.06756591796875,
    -0.01496124267578125,
    0.0017852783203125,
    0.016845703125,
    0.0309295654296875,
    -0.0304412841796875,
    -0.017181396484375,
    -0.0557861328125,
    0.00843048095703125,
    0.00927734375,
    -0.0423583984375,
    0.033111572265625,
    -3.641843795776367e-05,
    0.0091552734375,
    -0.0103759765625,
    -0.0008363723754882812,
    -0.022552490234375,
    0.049560546875,
    0.0160980224609375,
    -0.05548095703125,
    -0.04461669921875,
    0.0121917724609375,
    -0.0157928466796875,
    0.0028591156005859375,
    0.01088714599609375,
    -0.002918243408203125,
    0.0278167724609375,
    -0.01424407958984375,
    0.00811004638671875,
    -0.006641387939453125,
    0.08929443359375,
    0.0794677734375,
    0.00859832763671875,
    0.0164794921875,
    -0.002841949462890625,
    0.021087646484375,
    -0.05462646484375,
    -0.03363037109375,
    0.024658203125,
    -0.017913818359375,
    0.000682830810546875,
    -0.01139068603515625,
    -0.041961669921875,
    0.0070648193359375,
    0.032318115234375,
    0.002559661865234375,
    0.0104217529296875,
    0.01151275634765625,
    0.00928497314453125,
    -0.0250091552734375,
    -0.0285186767578125,
    0.05889892578125,
    0.0272674560546875,
    -0.049713134765625,
    -0.02679443359375,
    -0.03076171875,
    -0.025482177734375,
    -0.03741455078125,
    0.07086181640625,
    -0.015533447265625,
    0.0206451416015625,
    -0.05194091796875,
    -0.011138916015625,
    0.06903076171875,
    0.056182861328125,
    -0.0026607513427734375,
    -0.0268707275390625,
    -0.0306549072265625,
    0.01442718505859375,
    0.00615692138671875,
    0.03509521484375,
    -0.04083251953125,
    -0.01053619384765625,
    0.046142578125,
    -0.04248046875,
    0.005279541015625,
    -0.0001723766326904297,
    -0.016693115234375,
    0.0092315673828125,
    0.03350830078125,
    0.03155517578125,
    -0.00702667236328125,
    -0.0293731689453125,
    -0.02130126953125,
    -0.00815582275390625,
    0.0188751220703125,
    -0.01751708984375,
    0.0302734375,
    0.03948974609375,
    0.0052947998046875,
    0.017242431640625,
    0.0164337158203125,
    -0.0005726814270019531,
    0.01546478271484375,
    0.015960693359375,
    0.060760498046875,
    -0.01229095458984375,
    0.00815582275390625,
    0.007152557373046875,
    0.061676025390625,
    -0.035400390625,
    0.0259857177734375,
    -0.01137542724609375,
    0.017059326171875,
    0.059722900390625,
    -0.00595855712890625,
    0.01036834716796875,
    -0.0236968994140625,
    0.00914764404296875,
    0.01380157470703125,
    -0.019805908203125,
    -0.0169677734375,
    0.08819580078125,
    -0.009033203125,
    -0.01267242431640625,
    0.0287933349609375,
    0.01078033447265625,
    -0.041473388671875,
    0.010955810546875,
    0.01198577880859375,
    -0.0101776123046875,
    -0.004581451416015625,
    0.0127410888671875,
    -0.0126953125,
    -0.0338134765625,
    0.0218963623046875,
    0.06622314453125,
    0.05572509765625,
    0.0165863037109375,
    -0.0224151611328125,
    -0.0784912109375,
    0.01085662841796875,
    -0.00032830238342285156,
    -0.0219879150390625,
    0.053680419921875,
    0.025299072265625,
    -0.00431060791015625,
    0.040496826171875,
    0.005672454833984375,
    0.0287017822265625,
    0.0506591796875,
    -0.03924560546875,
    -0.033782958984375,
    0.02850341796875,
    0.00862884521484375,
    0.011260986328125,
    0.02557373046875,
    -0.048248291015625,
    -0.01385498046875,
    0.0020732879638671875,
    0.024505615234375,
    0.00992584228515625,
    -0.01209259033203125,
    -0.021209716796875,
    0.054443359375,
    -0.0293121337890625,
    -0.02685546875,
    -0.01375579833984375,
    -0.003032684326171875,
    0.0126800537109375,
    0.027374267578125,
    0.0055084228515625,
    0.0171051025390625,
    -0.03314208984375,
    -0.0321044921875,
    0.0054168701171875,
    -0.0389404296875,
    -0.0169677734375,
    -0.017578125,
    -0.0245208740234375,
    0.0141143798828125,
    0.05413818359375,
    0.033172607421875,
    0.0134735107421875,
    -0.00832366943359375,
    -0.017486572265625,
    -0.0618896484375,
    0.0230865478515625,
    -0.003627777099609375,
    0.00846099853515625,
    -0.048095703125,
    0.051483154296875,
    0.055145263671875,
    -0.006805419921875,
    -0.002643585205078125,
    0.0169677734375,
    -0.00395965576171875,
    -0.0071868896484375,
    -0.0144195556640625,
    -0.00638580322265625,
    -0.01508331298828125,
    0.0157470703125,
    -0.0008401870727539062,
    0.0139312744140625,
    0.048065185546875,
    -0.008880615234375,
    -0.001861572265625,
    0.06744384765625,
    0.01934814453125,
    -0.00734710693359375,
    0.03973388671875,
    0.0472412109375,
    -0.01183319091796875,
    -0.01220703125,
    -0.032379150390625,
    -0.0038013458251953125,
    -0.05096435546875,
    0.01329803466796875,
    -0.06280517578125,
    -0.0218353271484375,
    -4.410743713378906e-06,
    -0.004665374755859375,
    -0.02191162109375,
    -0.0189208984375,
    -0.03857421875,
    0.0218658447265625,
    -0.030914306640625,
    -0.00229644775390625,
    -0.005825042724609375,
    -0.0179443359375,
    0.0018777847290039062,
    0.01739501953125,
    0.05633544921875,
    -0.042510986328125,
    0.023773193359375,
    -0.006259918212890625,
    0.028411865234375,
    0.0234527587890625,
    0.01389312744140625,
    -0.033721923828125,
    0.0196533203125,
    0.0291900634765625,
    -0.00614166259765625,
    -0.0200653076171875,
    0.01436614990234375,
    0.00954437255859375,
    0.0306549072265625,
    0.010345458984375,
    -0.00823974609375,
    -0.0330810546875,
    -0.044097900390625,
    -0.0670166015625,
    0.0095062255859375,
    0.019622802734375,
    -0.06689453125,
    -0.03607177734375,
    -0.006366729736328125,
    0.0106353759765625,
    -0.0251617431640625,
    0.0272064208984375,
    -0.016082763671875,
    -0.004627227783203125,
    0.047119140625,
    -0.055999755859375,
    -0.022003173828125,
    -0.00839996337890625,
    0.032379150390625,
    0.05560302734375,
    0.005462646484375,
    0.03814697265625,
    -0.04461669921875,
    0.032501220703125,
    -0.01102447509765625,
    0.060699462890625,
    0.0086212158203125,
    0.034332275390625,
    -0.06085205078125,
    0.0044097900390625,
    -0.017578125,
    -0.006168365478515625,
    0.046844482421875,
    -0.031463623046875,
    0.00876617431640625,
    -0.00301361083984375,
    0.01035308837890625,
    0.06683349609375,
    -0.029693603515625,
    -0.0026149749755859375,
    0.05145263671875,
    -0.013336181640625,
    -0.018463134765625,
    0.0328369140625,
    0.02178955078125,
    -0.0201263427734375,
    0.037109375,
    0.007244110107421875,
    0.024749755859375,
    -0.01242828369140625,
    -0.00036597251892089844,
    0.00582122802734375,
    0.023712158203125,
    -0.016815185546875,
    -0.017181396484375,
    0.018402099609375,
    0.018341064453125,
    0.0236968994140625,
    -0.01548004150390625,
    0.00806427001953125,
    0.040191650390625,
    0.00804901123046875,
    -0.003284454345703125,
    -0.041015625,
    0.006038665771484375,
    0.01317596435546875,
    0.006610870361328125,
    0.0060577392578125,
    -0.005626678466796875,
    -0.01309967041015625,
    0.01763916015625,
    0.0209197998046875,
    0.0194549560546875,
    0.00666046142578125,
    0.0164794921875,
    -0.044281005859375,
    0.07733154296875,
    0.0628662109375,
    0.041656494140625,
    -0.04632568359375,
    0.0253143310546875,
    0.051849365234375,
    -0.0232696533203125,
    0.00273895263671875,
    0.0008873939514160156,
    0.0014505386352539062,
    -0.005916595458984375,
    -0.0226898193359375,
    -0.01032257080078125,
    -0.010772705078125,
    -0.02178955078125,
    0.032135009765625,
    0.0184326171875,
    -0.0256805419921875,
    -0.01238250732421875,
    0.035675048828125,
    -0.0029354095458984375,
    -0.0034770965576171875,
    0.06268310546875,
    -0.00931549072265625,
    -0.00841522216796875,
    0.028350830078125,
    -0.02093505859375,
    -0.00919342041015625,
    -0.0278778076171875,
    -0.031402587890625,
    0.0206451416015625,
    0.004486083984375,
    0.0113983154296875,
    0.03765869140625,
    0.02313232421875,
    0.0198211669921875,
    0.0012950897216796875,
    -0.0162811279296875,
    0.0008535385131835938,
    -0.0016984939575195312,
    -0.01102447509765625,
    -0.01380157470703125,
    0.041961669921875,
    -0.016021728515625,
    0.01435089111328125,
    0.03857421875,
    -0.01247406005859375,
    0.0209503173828125,
    -0.052703857421875,
    0.056610107421875,
    -0.06158447265625,
    -0.0172119140625,
    0.020477294921875,
    0.046051025390625,
    -0.0018320083618164062,
    -0.01953125,
    0.0140838623046875,
    -0.01303863525390625,
    -0.05682373046875,
    -0.017059326171875,
    0.03179931640625,
    0.02630615234375,
    -0.00016379356384277344,
    0.00652313232421875,
    0.037078857421875,
    -0.0245361328125,
    0.0296478271484375,
    -0.0452880859375,
    -0.003200531005859375,
    0.032745361328125,
    -0.0167694091796875,
    0.0187530517578125,
    0.0301361083984375,
    -0.0307464599609375,
    0.03094482421875,
    -0.038330078125,
    -0.0023670196533203125,
    -0.01093292236328125,
    0.047393798828125,
    0.00594329833984375,
    -0.006420135498046875,
    0.0028781890869140625,
    -0.0233917236328125,
    0.0011587142944335938,
    0.032745361328125,
    -0.00286865234375,
    0.0160064697265625,
    -0.008453369140625,
    0.022979736328125,
    0.00800323486328125,
    -0.017578125,
    0.02801513671875,
    0.00543975830078125,
    -0.059844970703125,
    -0.01561737060546875,
    0.0272216796875,
    0.0173797607421875,
    -0.0240020751953125,
    0.0089569091796875,
    0.09039306640625,
    0.01959228515625,
    0.01171112060546875,
    0.03887939453125,
    0.002532958984375,
    -0.0184326171875,
    -0.001667022705078125,
    -0.01073455810546875,
    -0.0120086669921875,
    -0.0194091796875,
    -0.043243408203125,
    0.033111572265625,
    0.0303192138671875,
    -0.0138702392578125,
    0.00969696044921875,
    0.03863525390625,
    0.020416259765625,
    0.01369476318359375,
    0.056182861328125,
    0.073974609375,
    0.0224151611328125,
    0.058807373046875,
    0.05450439453125,
    0.0273895263671875,
    -0.041534423828125,
    -0.038116455078125,
    -0.059967041015625,
    -0.03546142578125,
    -0.0126190185546875,
    -0.030426025390625,
    -0.0037708282470703125,
    0.00930023193359375,
    -0.0026760101318359375,
    0.0168609619140625,
    0.018157958984375,
    0.0204620361328125,
    0.01290130615234375,
    -0.004688262939453125,
    -0.01456451416015625,
    -0.07080078125,
    -0.07684326171875,
    0.0204010009765625,
    0.00922393798828125,
    -0.009307861328125,
    0.044830322265625,
    0.0010957717895507812,
    -0.00351715087890625,
    -0.0137786865234375,
    -0.1173095703125,
    -0.0216522216796875,
    0.11578369140625,
    0.03167724609375,
    -0.018341064453125,
    -0.0546875,
    0.0439453125,
    0.04718017578125,
    -0.0160980224609375,
    0.047882080078125,
    -0.0219573974609375,
    -0.05621337890625,
    -0.0233001708984375,
    -0.0283966064453125,
    0.0211029052734375,
    0.01036834716796875,
    -0.01108551025390625,
    -0.00911712646484375,
    0.006282806396484375,
    -0.033416748046875,
    -0.01568603515625,
    0.008880615234375,
    -0.03179931640625,
    -0.0035800933837890625,
    -0.021453857421875,
    -0.04931640625,
    0.012969970703125,
    -0.028472900390625,
    0.00319671630859375,
    -0.01739501953125,
    0.01446533203125,
    0.0152130126953125,
    0.02984619140625,
    -0.02349853515625,
    -0.01470947265625,
    -0.033477783203125,
    0.0535888671875,
    0.031707763671875,
    -0.00229644775390625,
    -0.016876220703125,
    0.040130615234375,
    0.02203369140625,
    0.0284881591796875,
    0.037139892578125,
    0.0150909423828125,
    0.00980377197265625,
    -0.0246734619140625,
    -0.042144775390625,
    -0.003520965576171875,
    -0.0187530517578125,
    -0.01519012451171875,
    -0.0240478515625,
    -0.032623291015625,
    -0.08721923828125,
    0.0023174285888671875,
    -0.004375457763671875,
    0.01192474365234375,
    0.056182861328125,
    -0.023345947265625,
    -0.04217529296875,
    -0.040771484375,
    -0.03302001953125,
    -0.05078125,
    -0.0122833251953125,
    -0.03900146484375,
    -0.0030574798583984375,
    -0.00948333740234375,
    0.00460052490234375,
    -0.0007486343383789062,
    -0.038970947265625,
    0.01557159423828125,
    0.0049285888671875,
    -0.055755615234375,
    0.0218353271484375,
    0.00928497314453125,
    -0.059173583984375,
    -0.0241851806640625,
    -0.0031909942626953125,
    -0.04608154296875,
    -0.020111083984375,
    0.004550933837890625,
    0.04302978515625,
    0.023162841796875,
    0.0037708282470703125,
    -0.023590087890625,
    -0.0238494873046875,
    0.0223541259765625,
    0.01067352294921875,
    0.040130615234375,
    -0.0435791015625,
    0.07806396484375,
    0.06658935546875,
    0.00830841064453125,
    0.005615234375,
    0.0872802734375,
    -0.02069091796875,
    0.00930023193359375,
    -0.0179901123046875,
    0.02679443359375,
    0.009490966796875,
    -0.03582763671875,
    0.024139404296875,
    0.042388916015625,
    0.007343292236328125,
    0.00460052490234375,
    0.0029926300048828125,
    0.0192108154296875,
    -0.003803253173828125,
    -0.0180816650390625,
    -0.01415252685546875,
    -0.00849151611328125,
    -0.02740478515625,
    -0.008392333984375,
    -0.053192138671875,
    0.026214599609375,
    0.01739501953125,
    0.015625,
    -0.11370849609375,
    0.007015228271484375,
    0.0310211181640625,
    -0.030487060546875,
    0.01248931884765625,
    0.062042236328125,
    -0.046905517578125,
    0.0239410400390625,
    -0.027496337890625,
    0.019866943359375,
    0.0672607421875,
    0.0312042236328125,
    -0.037994384765625,
    -0.057159423828125,
    0.01418304443359375,
    0.016143798828125,
    -0.0287933349609375,
    -0.0152740478515625,
    0.00270843505859375,
    0.0079345703125,
    0.0266571044921875,
    -0.03875732421875,
    0.039093017578125,
    0.033905029296875,
    -0.03607177734375,
    0.0433349609375,
    0.045440673828125,
    -0.01204681396484375,
    -0.039581298828125,
    0.03509521484375,
    -0.005924224853515625,
    -0.03131103515625,
    -0.0292205810546875,
    0.003276824951171875,
    -0.0207061767578125,
    -0.035125732421875,
    0.0036602020263671875,
    -0.023193359375,
    0.06146240234375,
    0.018096923828125,
    0.017974853515625,
    -0.0162353515625,
    -0.01136016845703125,
    0.043121337890625,
    0.005603790283203125,
    0.00847625732421875,
    0.03070068359375,
    -0.005352020263671875,
    -0.0340576171875,
    0.016204833984375,
    -0.031829833984375,
    -0.0208740234375,
    0.08074951171875,
    -0.018646240234375,
    0.067138671875,
    0.0020122528076171875,
    0.01154327392578125,
    -0.064453125,
    -0.0189056396484375,
    0.04302978515625,
    -0.01122283935546875,
    0.064208984375,
    -0.027557373046875,
    0.00899505615234375,
    0.0088348388671875,
    0.028961181640625,
    -0.031829833984375,
    -0.0014085769653320312,
    -0.01277923583984375,
    -0.0029773712158203125,
    -0.00844573974609375,
    0.032928466796875,
    -0.021697998046875,
    0.01175689697265625,
    0.01149749755859375,
    0.0174407958984375,
    -0.0634765625,
    -0.0089569091796875,
    -0.042388916015625,
    -0.009033203125,
    0.00748443603515625,
    -0.010223388671875,
    -0.0174560546875,
    0.0130157470703125,
    0.0156402587890625,
    -0.0166473388671875,
    0.023345947265625,
    0.007293701171875,
    -0.026763916015625,
    -0.00203704833984375,
    -0.0021190643310546875,
    -0.0273590087890625,
    0.004596710205078125,
    0.0105438232421875,
    -0.0509033203125,
    -0.032501220703125,
    0.0579833984375,
    -0.0134429931640625,
    -0.0621337890625,
    0.0234832763671875,
    0.02166748046875,
    -0.03167724609375,
    -0.005207061767578125,
    0.06707763671875,
    0.016876220703125,
    0.007167816162109375,
    0.054534912109375,
    -0.037567138671875,
    -0.021392822265625,
    -0.0248870849609375,
    0.005641937255859375,
    0.0070648193359375,
    -0.0215301513671875,
    -0.045318603515625,
    0.07244873046875,
    -0.0311126708984375,
    -0.045257568359375,
    0.003631591796875,
    0.0204925537109375,
    -0.0260009765625,
    -0.0443115234375,
    0.06231689453125,
    0.0301055908203125,
    -0.00962066650390625,
    0.026641845703125,
    -0.0089111328125,
    0.0250091552734375,
    0.02301025390625,
    0.022674560546875,
    -0.026123046875,
    0.0582275390625,
    0.035125732421875,
    -0.01505279541015625,
    0.0634765625,
    0.02734375,
    0.0034637451171875,
    -0.022857666015625,
    0.029815673828125,
    0.034027099609375,
    -0.0103607177734375,
    -0.0438232421875,
    -0.0229339599609375,
    -0.06292724609375,
    0.07958984375,
    0.024566650390625,
    -0.0038166046142578125,
    0.005950927734375,
    -0.0210418701171875,
    -0.01436614990234375,
    -0.02069091796875,
    0.031768798828125,
    0.0819091796875,
    0.007053375244140625,
    0.0124359130859375,
    -0.034149169921875,
    0.0182342529296875,
    -0.03350830078125,
    0.01971435546875,
    0.02252197265625,
    0.0010547637939453125,
    -0.031646728515625,
    0.025726318359375,
    0.01033782958984375,
    0.0853271484375,
    -0.004608154296875,
    0.0032405853271484375,
    0.0183563232421875,
    -0.026092529296875,
    0.0170440673828125,
    -0.018341064453125,
    0.005306243896484375,
    -0.0177154541015625,
    0.00392913818359375,
    -0.032958984375,
    -0.0401611328125,
    0.0109405517578125,
    -0.050201416015625,
    0.029022216796875,
    0.0006852149963378906,
    -0.02734375,
    0.0042572021484375,
    0.0361328125,
    -0.028778076171875,
    -0.0211029052734375,
    -0.0303192138671875,
    -0.04656982421875,
    0.01824951171875,
    -0.02716064453125,
    4.380941390991211e-05,
    -0.004337310791015625,
    0.033111572265625,
    -0.0012941360473632812,
    -0.0012664794921875,
    0.0153045654296875,
    0.03656005859375,
    -0.0200653076171875,
    0.00275421142578125,
    -0.055755615234375,
    -0.021636962890625,
    -0.0229034423828125,
    -0.047119140625,
    0.0287322998046875,
    -0.0226287841796875,
    -0.024688720703125,
    0.0584716796875,
    0.0535888671875,
    0.055419921875,
    0.0345458984375,
    0.017578125,
    -0.10052490234375,
    0.006473541259765625,
    -0.0262298583984375,
    -0.0248260498046875,
    -0.01123046875,
    0.0361328125,
    0.04345703125,
    -0.0357666015625,
    -0.042327880859375,
    0.01885986328125,
    -0.05426025390625,
    0.054840087890625,
    -0.001995086669921875,
    -0.01392364501953125,
    0.0166168212890625,
    0.024810791015625,
    0.05828857421875,
    -0.0013780593872070312,
    0.0239410400390625,
    -0.01165771484375,
    0.0261077880859375,
    0.0178070068359375,
    -0.034423828125,
    0.0207672119140625,
    -0.00374603271484375,
    -0.0184783935546875,
    0.047393798828125,
    -0.050506591796875,
    -0.0068359375,
    -0.013885498046875,
    -0.0218505859375,
    0.0219879150390625,
    -0.010406494140625,
    -0.0003273487091064453,
    0.033843994140625,
    -0.0211181640625,
    -0.0163726806640625,
    -0.002109527587890625,
    -0.0223236083984375,
    0.004306793212890625,
    -0.00432586669921875,
    -0.021087646484375,
    -0.02191162109375,
    0.00286865234375,
    0.00244140625,
    0.045166015625,
    -0.00656890869140625,
    0.0230255126953125,
    0.0036716461181640625,
    -0.01387786865234375,
    0.0028858184814453125,
    0.0010480880737304688,
    0.000904083251953125,
    0.0196380615234375,
    -0.0007281303405761719,
    -0.0084686279296875,
    -0.01043701171875,
    0.04248046875,
    0.038330078125,
    0.0247344970703125,
    0.045806884765625,
    -0.040435791015625,
    -0.01308441162109375,
    0.01418304443359375,
    -0.04888916015625,
    -0.0148162841796875,
    -0.00440216064453125,
    0.007183074951171875,
    0.0153045654296875,
    -0.0067138671875,
    0.040008544921875,
    -0.0024566650390625,
    -0.04327392578125,
    0.006549835205078125,
    0.043548583984375,
    0.03619384765625,
    -0.022735595703125,
    -0.0438232421875,
    -0.012664794921875,
    -0.0012140274047851562,
    -0.01544189453125,
    -0.037261962890625,
    -0.029327392578125,
    0.06463623046875,
    0.00037360191345214844,
    0.01035308837890625,
    0.0218963623046875,
    0.0100860595703125,
    0.00757598876953125,
    -0.00537872314453125,
    0.039642333984375,
    0.0018482208251953125,
    0.0162811279296875,
    0.018524169921875,
    -0.06097412109375,
    0.029083251953125,
    0.0097503662109375,
    -0.0638427734375,
    -0.06292724609375,
    0.0193328857421875,
    0.02691650390625,
    -0.0343017578125,
    -0.0189056396484375,
    0.021514892578125,
    0.045074462890625,
    -0.0108489990234375,
    0.004619598388671875,
    -0.02490234375,
    0.0266876220703125,
    -0.00023472309112548828,
    0.02337646484375,
    -0.0098876953125,
    0.0003237724304199219,
    0.05517578125,
    -0.037078857421875,
    0.06439208984375,
    -0.048370361328125,
    -0.0234832763671875,
    0.030975341796875,
    0.0282745361328125,
    -0.01291656494140625,
    0.00913238525390625,
    -0.024566650390625,
    -0.0308380126953125,
    0.004764556884765625,
    -0.035614013671875,
    0.048248291015625,
    0.045623779296875,
    -0.04638671875,
]

# here I need this
embedding_arr = array.array("f", embedding_vet)

with oracledb.connect(**CONNECT_ARGS) as conn:
    question = questions[0]

    query = f"""
    SELECT id, text, metadata,
    vector_distance(embedding, :embedding,
    COSINE) as distance
    FROM BOOKS
    ORDER BY distance
    FETCH APPROX FIRST 6 ROWS ONLY
    """

    with conn.cursor() as cursor:
        cursor.execute(query, embedding=embedding_arr)

        rows = cursor.fetchall()

        for row in rows:
            print(row[0])
