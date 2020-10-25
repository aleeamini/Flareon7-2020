using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using ExifLib;
using System.Resources;
using System.Security.Cryptography;
namespace ConsoleApp2
{
    class Program
    {
		private bool isHome = false;
		public static string Desc { get; set; }
		public static string Note { get; set; }
		public static string Step { get; set; }
		public static string Password { get; set; }
		public static double TPKLat { get; set; }
		public static double TPKLon { get; set; }
		public static byte[] ImgData { get; set; }

		
		public static string Decode(byte[] e)
		{
			string text = "";
			foreach (byte b in e)
			{
				text += Convert.ToChar((int)(b ^ 83)).ToString();
			}
			return text;
		}
		public static string GetString(byte[] cipherText, byte[] Key, byte[] IV)
		{
			string result = null;
			using (RijndaelManaged rijndaelManaged = new RijndaelManaged())
			{
				rijndaelManaged.Key = Key;
				rijndaelManaged.IV = IV;
				ICryptoTransform cryptoTransform = rijndaelManaged.CreateDecryptor(rijndaelManaged.Key, rijndaelManaged.IV);
				using (MemoryStream memoryStream = new MemoryStream(cipherText))
				{
					using (CryptoStream cryptoStream = new CryptoStream(memoryStream, cryptoTransform, 0))
					{
						using (StreamReader streamReader = new StreamReader(cryptoStream))
						{
							result = streamReader.ReadToEnd();
						}
					}
				}
			}
			return result;
		}
		
		public static double[] GetCoordinates(string imageFileName)
		{
			double[] result;
			using (ExifReader exifReader = new ExifReader(imageFileName))
			{
				string text = "";
				string text2 = "";
				double[] array;
				double[] array2;
				if (exifReader.GetTagValue<double[]>(ExifTags.GPSLatitude, out array) && exifReader.GetTagValue<double[]>(ExifTags.GPSLongitude, out array2) && exifReader.GetTagValue<string>(ExifTags.GPSLatitudeRef, out text) && exifReader.GetTagValue<string>(ExifTags.GPSLongitudeRef, out text2))
				{
					double num = array2[0] + array2[1] / 60.0 + array2[2] / 3600.0;
					double num2 = array[0] + array[1] / 60.0 + array[2] / 3600.0;
					result = new double[]
					{
						(double)(text.StartsWith("N") ? 1 : -1) * num2,
						(double)(text2.StartsWith("E") ? 1 : -1) * num
					};
				}
				else
				{
					result = new double[2];
				}
			}
			return result;
		}
		private void CheckHome()
		{
			double Latitude = 0;
			double Longitude = 0;
			double num = 1.0;
			//Location location = TodoPage._locator.GetLocation();
			if (this.GetHowFar(TPKLat, TPKLon, Latitude, Longitude) < num)
			{
				this.isHome = true;
			}
			else
			{
				this.isHome = false;
			}

		}
		public double GetHowFar(double longitude, double latitude, double otherLongitude, double otherLatitude)
		{
			double num = latitude * 0.017453292519943295;
			double num2 = longitude * 0.017453292519943295;
			double num3 = otherLatitude * 0.017453292519943295;
			double num4 = otherLongitude * 0.017453292519943295 - num2;
			double num5 = Math.Pow(Math.Sin((num3 - num) / 2.0), 2.0) + Math.Cos(num) * Math.Cos(num3) * Math.Pow(Math.Sin(num4 / 2.0), 2.0);
			return 6376500.0 * (2.0 * Math.Atan2(Math.Sqrt(num5), Math.Sqrt(1.0 - num5))) * 0.000621371;
		}
		internal static byte[] Runtime_dll
		{
			get
			{
				return (byte[]) ConsoleApp2.Resource1.ResourceManager.GetObject("Runtime.dll");
			}
		}
		public static bool GetImage()
		{
			
			string text = new string(new char[]
			{
				Desc[2],
				Password[6],
				Password[4],
				Note[4],
				Note[0],
				Note[17],
				Note[18],
				Note[16],
				Note[11],
				Note[13],
				Note[12],
				Note[15],
				Step[4],
				Password[6],
				Desc[1],
				Password[2],
				Password[2],
				Password[4],
				Note[18],
				Step[2],
				Password[4],
				Note[5],
				Note[4],
				Desc[0],
				Desc[3],
				Note[15],
				Note[8],
				Desc[4],
				Desc[3],
				Note[4],
				Step[2],
				Note[13],
				Note[18],
				Note[18],
				Note[8],
				Note[4],
				Password[0],
				Password[7],
				Note[0],
				Password[4],
				Note[11],
				Password[6],
				Password[4],
				Desc[4],
				Desc[3]
			});
			byte[] key = SHA256.Create().ComputeHash(Encoding.ASCII.GetBytes(text));
			byte[] bytes = Encoding.ASCII.GetBytes("NoSaltOfTheEarth");
			try
			{
				byte[] rt = Runtime_dll;
				ImgData = Convert.FromBase64String(GetString(Runtime_dll, key, bytes));
				return true;
			}
			catch (Exception ex)
			{
				
			}
			return false;
		}
		static void Main(string[] args)
        {
			byte[] Pass = new byte[]
			{
				62,
				38,
				63,
				63,
				54,
				39,
				59,
				50,
				39
			};
			
			Password=Decode(Pass);
			Note = "keep steaks for dinner";
			Step = "magic";
			using (ExifReader exifReader = new ExifReader("C:\\Users\\Me\\Desktop\\flareon2020\\5\\TKApp\\res\\gallery\\05.jpg"))
			{
				string desc;
				if (exifReader.GetTagValue<string>(ExifTags.ImageDescription, out desc))
				{
					Desc = desc;
				}
				else
				{
					Desc = "";
				}
			}
			GetImage();
			using (BinaryWriter binWriter = new BinaryWriter(File.Open("Runtime.jpg", FileMode.Create)))
			{
				
				binWriter.Write(ImgData);
				
			}
			double[] coordinates = GetCoordinates("C:\\Users\\Me\\Desktop\\flareon2020\\5\\TKApp\\res\\gallery\\04.jpg");
			TPKLat = coordinates[0];
			TPKLon = coordinates[1];
			
			
			Console.ReadLine();
        }
    }
}
