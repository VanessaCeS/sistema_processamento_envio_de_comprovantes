import unittest
import rotina_contra_cheque
import os

class TestDividirERenomearPDF(unittest.TestCase):
    def setUp(self):
        os.makedirs('arquivos_pdf_temp')
        os.makedirs('arquivos_txt_temp')

    def tearDown(self):
        import shutil
        shutil.rmtree('arquivos_pdf_temp')
        shutil.rmtree('arquivos_txt_temp')

    def test_dividir_e_renomear_pdf_contra_cheque(self):
        caminho_pdf = 'pdfs/CONTRA_CHEQUE_2.PDF'
        mes_referencia = '22-06-2022'  
        
        resultado =  rotina_contra_cheque.dividir_e_renomear_pdf_contra_cheque(caminho_pdf, mes_referencia)
        
        self.assertTrue(os.path.exists('arquivos_pdf_temp/ANA JULIA ALVES DE SOUSA - JUNHO 22.pdf'))
        self.assertTrue(os.path.exists('arquivos_txt_temp/contra_cheque_0.txt'))
        
        self.assertIsInstance(resultado, tuple)
        self.assertEqual(resultado[0], "Sucesso")
        self.assertIsInstance(resultado[1], int)
      
if __name__ == '__main__':
    unittest.main()
