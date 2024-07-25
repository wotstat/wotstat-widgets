package wotstat.widgets {
  import flash.utils.ByteArray;
  import flash.utils.Endian;

  public class Utils {

    // https://rtmp.veriskope.com/pdf/amf3-file-format-spec.pdf
    public static function readU29V(bytes:ByteArray):Object {
      var value:int = 0;
      var byte:int = 0;

      do {
        byte = bytes.readUnsignedByte();
        value <<= 7;
        value |= (byte & 0x7F);
      }
      while ((byte & 0x80) != 0);

      return {value: value >> 1, flag: (value & 0x1) == 1};
    }

    public static function decodeIntArrayLoop(data:Array.<uint>, shift:int):ByteArray {
      var output:ByteArray = new ByteArray();
      output.endian = Endian.BIG_ENDIAN;

      for (var i:int = 0; i < data.length - (shift > 0 ? 1 : 0); ++i) {
        output.writeUnsignedInt(new uint(data[i]));
      }

      if (shift > 0) {
        var lastPart:int = data[data.length - 1];
        if (shift == 1) {
          output.writeByte(lastPart >> 24);
          output.writeByte(lastPart >> 16);
          output.writeByte(lastPart >> 8);
        }
        else if (shift == 2) {
          output.writeByte(lastPart >> 24);
          output.writeByte(lastPart >> 16);
        }
        else if (shift == 3) {
          output.writeByte(lastPart >> 24);
        }
      }

      output.position = 0;
      return output;
    }

    // https://rtmp.veriskope.com/pdf/amf3-file-format-spec.pdf
    public static function decodeIntArrayAMF(array:Array, shift:int = 0):ByteArray {
      var testVector:Vector.<uint> = Vector.<uint>(array);

      var tempBytes:ByteArray = new ByteArray();
      tempBytes.writeObject(testVector);
      tempBytes.position = 0;

      tempBytes.readUnsignedByte(); // marker
      readU29V(tempBytes); // length
      tempBytes.readUnsignedByte(); // flag

      var result:ByteArray = new ByteArray();
      result.writeBytes(tempBytes, tempBytes.position, tempBytes.bytesAvailable - shift);

      return result;
    }

    public static function byteArrayToHex(bytes:ByteArray, offset:int = 0):String {
      var str:String = "";
      for (var i:int = offset; i < bytes.length; ++i) {
        var hexString:String = bytes[i].toString(16);
        if (hexString.length == 1) {
          hexString = "0" + hexString;
        }
        str += hexString;

      }
      return str;
    }

    public static function decodeBase64(base64:String):ByteArray {
      var lookup:String = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
      var output:ByteArray = new ByteArray();

      var i:int = 0;
      var enc1:int, enc2:int, enc3:int, enc4:int;
      var chr1:int, chr2:int, chr3:int;

      while (i < base64.length) {
        enc1 = lookup.indexOf(base64.charAt(i++ ));
        enc2 = lookup.indexOf(base64.charAt(i++ ));
        enc3 = lookup.indexOf(base64.charAt(i++ ));
        enc4 = lookup.indexOf(base64.charAt(i++ ));

        chr1 = (enc1 << 2) | (enc2 >> 4);
        chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
        chr3 = ((enc3 & 3) << 6) | enc4;

        output.writeByte(chr1);
        if (enc3 != 64)
          output.writeByte(chr2);
        if (enc4 != 64)
          output.writeByte(chr3);
      }

      output.position = 0;
      return output;
    }
  }
}