# #################################################################################################################### #
# Imports                                                                                                              #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #
import os
from socket import *
import struct
import time
import select


# #################################################################################################################### #
# Class IcmpHelperLibrary                                                                                              #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #
class IcmpHelperLibrary:
    # ################################################################################################################ #
    # Class IcmpPacket                                                                                                 #
    #                                                                                                                  #
    # References:                                                                                                      #
    # https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml                                           #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    class IcmpPacket:
        # ############################################################################################################ #
        # IcmpPacket Class Scope Variables                                                                             #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        __icmpTarget = ""               # Remote Host
        __destinationIpAddress = ""     # Remote Host IP Address
        __header = b''                  # Header after byte packing
        __data = b''                    # Data after encoding
        __dataRaw = ""                  # Raw string data before encoding
        __icmpType = 0                  # Valid values are 0-255 (unsigned int, 8 bits)
        __icmpCode = 0                  # Valid values are 0-255 (unsigned int, 8 bits)
        __packetChecksum = 0            # Valid values are 0-65535 (unsigned short, 16 bits)
        __packetIdentifier = 0          # Valid values are 0-65535 (unsigned short, 16 bits)
        __packetSequenceNumber = 0      # Valid values are 0-65535 (unsigned short, 16 bits)
        __ipTimeout = 10
        __ttl = 255                     # Time to live
        __rtt = 0

        __DEBUG_IcmpPacket = False      # Allows for debug output

        # ############################################################################################################ #
        # IcmpPacket Class Getters                                                                                     #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def getIcmpTarget(self):
            return self.__icmpTarget

        def getDataRaw(self):
            return self.__dataRaw

        def getIcmpType(self):
            return self.__icmpType

        def getIcmpCode(self):
            return self.__icmpCode

        def getPacketChecksum(self):
            return self.__packetChecksum

        def getPacketIdentifier(self):
            return self.__packetIdentifier

        def getPacketSequenceNumber(self):
            return self.__packetSequenceNumber

        def getTtl(self):
            return self.__ttl
        
        def getRtt(self):
            return self.__rtt

        # ############################################################################################################ #
        # IcmpPacket Class Setters                                                                                     #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def setIcmpTarget(self, icmpTarget):
            self.__icmpTarget = icmpTarget

            # Only attempt to get destination address if it is not whitespace
            if len(self.__icmpTarget.strip()) > 0:
                self.__destinationIpAddress = gethostbyname(self.__icmpTarget.strip())

        def setIcmpType(self, icmpType):
            self.__icmpType = icmpType

        def setIcmpCode(self, icmpCode):
            self.__icmpCode = icmpCode

        def setPacketChecksum(self, packetChecksum):
            self.__packetChecksum = packetChecksum

        def setPacketIdentifier(self, packetIdentifier):
            self.__packetIdentifier = packetIdentifier

        def setPacketSequenceNumber(self, sequenceNumber):
            self.__packetSequenceNumber = sequenceNumber

        def setTtl(self, ttl):
            self.__ttl = ttl
        
        def setRtt(self, rtt):
            self.__rtt = rtt

        # ############################################################################################################ #
        # IcmpPacket Class Private Functions                                                                           #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def __recalculateChecksum(self):
            print("calculateChecksum Started...") if self.__DEBUG_IcmpPacket else 0
            packetAsByteData = b''.join([self.__header, self.__data])
            checksum = 0

            # This checksum function will work with pairs of values with two separate 16 bit segments. Any remaining
            # 16 bit segment will be handled on the upper end of the 32 bit segment.
            countTo = (len(packetAsByteData) // 2) * 2

            # Calculate checksum for all paired segments
            print(f'{"Count":10} {"Value":10} {"Sum":10}') if self.__DEBUG_IcmpPacket else 0
            count = 0
            while count < countTo:
                thisVal = packetAsByteData[count + 1] * 256 + packetAsByteData[count]
                checksum = checksum + thisVal
                checksum = checksum & 0xffffffff        # Capture 16 bit checksum as 32 bit value
                print(f'{count:10} {hex(thisVal):10} {hex(checksum):10}') if self.__DEBUG_IcmpPacket else 0
                count = count + 2

            # Calculate checksum for remaining segment (if there are any)
            if countTo < len(packetAsByteData):
                thisVal = packetAsByteData[len(packetAsByteData) - 1]
                checksum = checksum + thisVal
                checksum = checksum & 0xffffffff        # Capture as 32 bit value
                print(count, "\t", hex(thisVal), "\t", hex(checksum)) if self.__DEBUG_IcmpPacket else 0

            # Add 1's Complement Rotation to original checksum
            checksum = (checksum >> 16) + (checksum & 0xffff)   # Rotate and add to base 16 bits
            checksum = (checksum >> 16) + checksum              # Rotate and add

            answer = ~checksum                  # Invert bits
            answer = answer & 0xffff            # Trim to 16 bit value
            answer = answer >> 8 | (answer << 8 & 0xff00)
            print("Checksum: ", hex(answer)) if self.__DEBUG_IcmpPacket else 0

            self.setPacketChecksum(answer)

        def __packHeader(self):
            # The following header is based on http://www.networksorcery.com/enp/protocol/icmp/msg8.htm
            # Type = 8 bits
            # Code = 8 bits
            # ICMP Header Checksum = 16 bits
            # Identifier = 16 bits
            # Sequence Number = 16 bits
            self.__header = struct.pack("!BBHHH",
                                   self.getIcmpType(),              #  8 bits / 1 byte  / Format code B
                                   self.getIcmpCode(),              #  8 bits / 1 byte  / Format code B
                                   self.getPacketChecksum(),        # 16 bits / 2 bytes / Format code H
                                   self.getPacketIdentifier(),      # 16 bits / 2 bytes / Format code H
                                   self.getPacketSequenceNumber()   # 16 bits / 2 bytes / Format code H
                                   )

        def __encodeData(self):
            data_time = struct.pack("d", time.time())               # Used to track overall round trip time
                                                                    # time.time() creates a 64 bit value of 8 bytes
            dataRawEncoded = self.getDataRaw().encode("utf-8")

            self.__data = data_time + dataRawEncoded

        def __packAndRecalculateChecksum(self):
            # Checksum is calculated with the following sequence to confirm data in up to date
            self.__packHeader()                 # packHeader() and encodeData() transfer data to their respective bit
                                                # locations, otherwise, the bit sequences are empty or incorrect.
            self.__encodeData()
            self.__recalculateChecksum()        # Result will set new checksum value
            self.__packHeader()                 # Header is rebuilt to include new checksum value

        def __validateIcmpReplyPacketWithOriginalPingData(self, icmpReplyPacket):
            # Check if the sequence number is valid
            if self.getPacketSequenceNumber() != icmpReplyPacket.getIcmpSequenceNumber():
                icmpReplyPacket.setIcmpSequenceNumberIsValid(False)
            else:
                icmpReplyPacket.setIcmpSequenceNumberIsValid(True)

            # Check if the identifier is valid
            if self.getPacketIdentifier() != icmpReplyPacket.getIcmpIdentifier():
                icmpReplyPacket.setIcmpIdentifierIsValid(False)
            else:
                icmpReplyPacket.setIcmpIdentifierIsValid(True)

            # Check if the raw data is valid
            if self.getDataRaw() != icmpReplyPacket.getIcmpDataRaw():
                icmpReplyPacket.setIcmpRawDataIsValid(False)
            else:
                icmpReplyPacket.setIcmpRawDataIsValid(True)

            # Check if the overall response packet is valid
            if icmpReplyPacket.getIcmpSequenceNumberIsValid() and icmpReplyPacket.getIcmpIdentifierIsValid() and icmpReplyPacket.getIcmpRawDataIsValid():
                icmpReplyPacket.setIsValidResponse(True)
            else:
                icmpReplyPacket.setIsValidResponse(False)

            print("Is Valid ICMP Reply Packet: ", icmpReplyPacket.isValidResponse()) if self.__DEBUG_IcmpPacket else 0
            print("Expected Sequence Number: ", self.getPacketSequenceNumber(), "Recieved: ", icmpReplyPacket.getIcmpSequenceNumber()) if self.__DEBUG_IcmpPacket else 0
            print("Expected Identifier: ", self.getPacketIdentifier(), "Recieved: ", icmpReplyPacket.getIcmpIdentifier()) if self.__DEBUG_IcmpPacket else 0
            print("Expected Data Raw: ", self.getDataRaw(), "Recieved: ", icmpReplyPacket.getIcmpDataRaw()) if self.__DEBUG_IcmpPacket else 0

        # ############################################################################################################ #
        # IcmpPacket Class Public Functions                                                                            #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def buildPacket_echoRequest(self, packetIdentifier, packetSequenceNumber):
            self.setIcmpType(8)
            self.setIcmpCode(0)
            self.setPacketIdentifier(packetIdentifier)
            self.setPacketSequenceNumber(packetSequenceNumber)
            self.__dataRaw = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            self.__packAndRecalculateChecksum()

        # Refactored to return ICMP type and code for message conversion
        def sendEchoRequest(self, silent=False):
            if len(self.__icmpTarget.strip()) <= 0 | len(self.__destinationIpAddress.strip()) <= 0:
                self.setIcmpTarget("127.0.0.1")

            if not silent:
                print("Pinging (" + self.__icmpTarget + ") " + self.__destinationIpAddress)

            mySocket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
            mySocket.settimeout(self.__ipTimeout)
            mySocket.bind(("", 0))
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', self.getTtl()))  # Unsigned int - 4 bytes
            try:
                mySocket.sendto(b''.join([self.__header, self.__data]), (self.__destinationIpAddress, 0))
                timeLeft = 10
                pingStartTime = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                endSelect = time.time()
                howLongInSelect = (endSelect - startedSelect)
                if whatReady[0] == []:  # Timeout
                    if not silent:
                        print("  *        *        *        *        *    Request timed out.")
                    return None
                recvPacket, addr = mySocket.recvfrom(1024)  # recvPacket - bytes object representing data received
                # addr  - address of socket sending data
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    if not silent:
                        print("  *        *        *        *        *    Request timed out (By no remaining time left).")
                    return None

                else:
                    # Fetch the ICMP type and code from the received packet
                    icmpType, icmpCode = recvPacket[20:22]
                    rtt = (timeReceived - pingStartTime) * 1000

                    if icmpType == 11:                          # Time Exceeded
                        icmpMessage = IcmpHelperLibrary.convertIcmpMessage(icmpType, icmpCode)
                        if not silent:
                            print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    Message=%s    %s" %
                                    (
                                        self.getTtl(),
                                        rtt,
                                        icmpType,
                                        icmpCode,
                                        icmpMessage,
                                        addr[0]
                                    )
                                  )
                        return {'type': icmpType, 'code': icmpCode, 'addr': addr[0], 'rtt': rtt}

                    elif icmpType == 3:                         # Destination Unreachable
                        icmpMessage = IcmpHelperLibrary.convertIcmpMessage(icmpType, icmpCode)
                        if not silent:
                            print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    Message=%s    %s" %
                                      (
                                          self.getTtl(),
                                          rtt,
                                          icmpType,
                                          icmpCode,
                                          icmpMessage,
                                          addr[0]
                                      )
                                    )
                        return {'type': icmpType, 'code': icmpCode, 'addr': addr[0], 'rtt': rtt}

                    elif icmpType == 0:                         # Echo Reply
                        icmpReplyPacket = IcmpHelperLibrary.IcmpPacket_EchoReply(recvPacket)
                        self.__validateIcmpReplyPacketWithOriginalPingData(icmpReplyPacket)
                        bytes = struct.calcsize("d")
                        timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                        self.setRtt((timeReceived - timeSent) * 1000)
                        if not silent:
                            icmpReplyPacket.printResultToConsole(self.getTtl(), timeReceived, addr, self) 
                        return {'type': icmpType, 'code': icmpCode, 'addr': addr[0], 'rtt': self.getRtt(), 'valid': icmpReplyPacket.isValidResponse()}

                    else:
                        if not silent:
                            print("error")
                        return None
            except timeout:
                if not silent:
                    print("  *        *        *        *        *    Request timed out (By Exception).")
                return None
            finally:
                mySocket.close()

        def printIcmpPacketHeader_hex(self):
            print("Header Size: ", len(self.__header))
            for i in range(len(self.__header)):
                print("i=", i, " --> ", self.__header[i:i+1].hex())

        def printIcmpPacketData_hex(self):
            print("Data Size: ", len(self.__data))
            for i in range(len(self.__data)):
                print("i=", i, " --> ", self.__data[i:i + 1].hex())

        def printIcmpPacket_hex(self):
            print("Printing packet in hex...")
            self.printIcmpPacketHeader_hex()
            self.printIcmpPacketData_hex()

    # ################################################################################################################ #
    # Class IcmpPacket_EchoReply                                                                                       #
    #                                                                                                                  #
    # References:                                                                                                      #
    # http://www.networksorcery.com/enp/protocol/icmp/msg0.htm                                                         #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    class IcmpPacket_EchoReply:
        # ############################################################################################################ #
        # IcmpPacket_EchoReply Class Scope Variables                                                                   #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        __recvPacket = b''
        __isValidResponse = False
        __IcmpSequenceNumber_IsValid = False
        __IcmpIdentifier_IsValid = False
        __IcmpRawData_IsValid = False

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Constructors                                                                            #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def __init__(self, recvPacket):
            self.__recvPacket = recvPacket

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Getters                                                                                 #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def getIcmpType(self):
            # Method 1
            # bytes = struct.calcsize("B")        # Format code B is 1 byte
            # return struct.unpack("!B", self.__recvPacket[20:20 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("B", 20)

        def getIcmpCode(self):
            # Method 1
            # bytes = struct.calcsize("B")        # Format code B is 1 byte
            # return struct.unpack("!B", self.__recvPacket[21:21 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("B", 21)

        def getIcmpHeaderChecksum(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[22:22 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 22)

        def getIcmpIdentifier(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[24:24 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 24)

        def getIcmpSequenceNumber(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[26:26 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 26)

        def getDateTimeSent(self):
            # This accounts for bytes 28 through 35 = 64 bits
            return self.__unpackByFormatAndPosition("d", 28)   # Used to track overall round trip time
                                                               # time.time() creates a 64 bit value of 8 bytes

        def getIcmpDataRaw(self):
            # This accounts for bytes 36 to the end of the packet.
            return self.__recvPacket[36:].decode('utf-8')

        def getIcmpSequenceNumberIsValid(self):
            return self.__IcmpSequenceNumber_IsValid

        def getIcmpIdentifierIsValid(self):
            return self.__IcmpIdentifier_IsValid
        
        def getIcmpRawDataIsValid(self):
            return self.__IcmpRawData_IsValid
        
        def isValidResponse(self):
            return self.__isValidResponse

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Setters                                                                                 #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def setIsValidResponse(self, booleanValue):
            self.__isValidResponse = booleanValue

        def setIcmpIdentifierIsValid(self, booleanValue):
            self.__IcmpIdentifier_IsValid = booleanValue
        
        def setIcmpSequenceNumberIsValid(self, booleanValue):
            self.__IcmpSequenceNumber_IsValid = booleanValue
        
        def setIcmpRawDataIsValid(self, booleanValue):
            self.__IcmpRawData_IsValid = booleanValue
        
        # ############################################################################################################ #
        # IcmpPacket_EchoReply Private Functions                                                                       #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def __unpackByFormatAndPosition(self, formatCode, basePosition):
            numberOfbytes = struct.calcsize(formatCode)
            return struct.unpack("!" + formatCode, self.__recvPacket[basePosition:basePosition + numberOfbytes])[0]

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Public Functions                                                                        #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def printResultToConsole(self, ttl, timeReceived, addr, IcmpEchoRequest):
            bytes = struct.calcsize("d")
            timeSent = struct.unpack("d", self.__recvPacket[28:28 + bytes])[0]
            icmpMessage = IcmpHelperLibrary.convertIcmpMessage(self.getIcmpType(), self.getIcmpCode())
            print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    Message=%s       Identifier=%d    Sequence Number=%d    %s" %
                  (
                      ttl,
                      (timeReceived - timeSent) * 1000,
                      self.getIcmpType(),
                      self.getIcmpCode(),
                      icmpMessage,
                      self.getIcmpIdentifier(),
                      self.getIcmpSequenceNumber(),
                      addr[0]
                  )
                 )
            print("--------------------------------")
            print("Echo Response Valid: ", self.isValidResponse())
            if not self.isValidResponse():
                if not self.getIcmpSequenceNumberIsValid():
                    print("Expected Sequence Number: ", IcmpEchoRequest.getPacketSequenceNumber(), "Recieved: ", self.getIcmpSequenceNumber())
                if not self.getIcmpIdentifierIsValid():
                    print("Expected Identifier: ", IcmpEchoRequest.getPacketIdentifier(), "Recieved: ", self.getIcmpIdentifier())
                if not self.getIcmpRawDataIsValid():
                    print("Expected Data Raw: ", IcmpEchoRequest.getDataRaw(), "Recieved: ", self.getIcmpDataRaw())

        def printIcmpReplyPacketSequenceNumber(self):
            print("IcmpSequenceNumber: ", self.getIcmpSequenceNumber())
        
        def printIcmpReplyPacketIdentifier(self):
            print("IcmpIdentifier: ", self.getIcmpIdentifier())
        
        def printIcmpReplyPacketDataRaw(self):
            print("IcmpDataRaw: ", self.getIcmpDataRaw())

    # ################################################################################################################ #
    # Class IcmpHelperLibrary                                                                                          #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #

    # ################################################################################################################ #
    # IcmpHelperLibrary Class Scope Variables                                                                          #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    __DEBUG_IcmpHelperLibrary = False                  # Allows for debug output

    # ################################################################################################################ #
    # IcmpHelperLibrary Private Functions                                                                              #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __sendIcmpEchoRequest(self, host):
        print("sendIcmpEchoRequest Started...") if self.__DEBUG_IcmpHelperLibrary else 0

        totalRtt = []
        totalPackets = 4
        totalPacketsReceived = 0

        for i in range(totalPackets):
            # Build packet
            icmpPacket = IcmpHelperLibrary.IcmpPacket()

            randomIdentifier = (os.getpid() & 0xffff)      # Get as 16 bit number - Limit based on ICMP header standards
                                                           # Some PIDs are larger than 16 bit

            packetIdentifier = randomIdentifier
            packetSequenceNumber = i

            icmpPacket.buildPacket_echoRequest(packetIdentifier, packetSequenceNumber)  # Build ICMP for IP payload
            icmpPacket.setIcmpTarget(host)

            # Send echo request, returns dict with response details or None if timeout
            result = icmpPacket.sendEchoRequest()                                                # Build IP
            if result and result['type'] == 0 and result['valid']:  # type 0 = Echo Reply
                totalRtt.append(result['rtt'])
                totalPacketsReceived += 1

            icmpPacket.printIcmpPacketHeader_hex() if self.__DEBUG_IcmpHelperLibrary else 0
            icmpPacket.printIcmpPacket_hex() if self.__DEBUG_IcmpHelperLibrary else 0
            # we should be confirming values are correct, such as identifier and sequence number and data
        print(f"\n--- {host} ping statistics ---")

        # Calculate packet loss rate
        packetsLost = totalPackets - totalPacketsReceived
        packetLossRate = (packetsLost / totalPackets) * 100 if totalPackets > 0 else 0
        print(f"{totalPackets} packets transmitted, {totalPacketsReceived} packets received, {packetLossRate:.2f}% packet loss")

        # Calculate min, max, and avg RTT
        if totalRtt:
            minRtt = min(totalRtt)
            maxRtt = max(totalRtt)
            avgRtt = sum(totalRtt) / len(totalRtt)
        else:
            minRtt = 0
            maxRtt = 0
            avgRtt = 0

        print(f"round-trip min/avg/max = {minRtt:.3f}ms/{avgRtt:.3f}ms/{maxRtt:.3f}ms")

    def __sendIcmpTraceRoute(self, host):
        print("sendIcmpTraceRoute Started...") if self.__DEBUG_IcmpHelperLibrary else 0

        maxHops = 64
        reached_destination = False

        # Get the destination IP address
        try:
            dest_ip = gethostbyname(host)
            print(f"traceroute to {host} ({dest_ip}), {maxHops} hops max")
        except:
            print(f"traceroute to {host}, {maxHops} hops max")
        
        for ttl in range(1, maxHops + 1):
            # Build packet
            icmpPacket = IcmpHelperLibrary.IcmpPacket()
            
            randomIdentifier = (os.getpid() & 0xffff)
            packetIdentifier = randomIdentifier
            packetSequenceNumber = 1
            
            icmpPacket.buildPacket_echoRequest(packetIdentifier, packetSequenceNumber)
            icmpPacket.setIcmpTarget(host)
            # Set increasing TTL
            icmpPacket.setTtl(ttl)
            
            # Send echo request, returns dict with response details or None if timeout
            result = icmpPacket.sendEchoRequest(silent=True) # Use silent=True for traceroute
            if result:
                # Echo Reply
                if result['type'] == 0:
                    # Valid echo reply - we reached the destination
                    print(f"{ttl:2d}  {result['addr']}  {result['rtt']:.0f} ms")
                    reached_destination = True
                    break
                # Destination Unreachable
                elif result['type'] == 3:
                    # Destination unreachable - we can't reach the destination
                    print(f"{ttl:2d}  {result['addr']}  {result['rtt']:.0f} ms  Destination Unreachable")
                    break
                # Time exceeded
                elif result['type'] == 11:
                    # Time exceeded - this is a hop on the route
                    print(f"{ttl:2d}  {result['addr']}  {result['rtt']:.0f} ms")

            else:
                # Timeout or error
                print(f"{ttl:2d}  * * *  Request timed out.")
        
        if not reached_destination:
            print("Trace complete.")
        else:
            print("Trace complete - destination reached.")

    # ################################################################################################################ #
    # IcmpHelperLibrary Public Functions                                                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def sendPing(self, targetHost):
        print("ping Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        self.__sendIcmpEchoRequest(targetHost)

    def traceRoute(self, targetHost):
        print("traceRoute Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        self.__sendIcmpTraceRoute(targetHost)

    # static method to convert ICMP type and code to human-readable message
    @staticmethod
    def convertIcmpMessage(icmpType, icmpCode):
        errorMessages = {
            0: {  # Echo Reply
                0: "Echo Reply"
            },
            3: {  # Destination Unreachable
                0: "Destination Network Unreachable",
                1: "Destination Host Unreachable",
                2: "Destination Protocol Unreachable", 
                3: "Destination Port Unreachable",
                4: "Fragmentation Required and Don't Fragment was Set",
                5: "Source Route Failed",
                6: "Destination Network Unknown",
                7: "Destination Host Unknown",
                8: "Source Host Isolated",
                9: "Communication with Destination Network is Administratively Prohibited",
                10: "Communication with Destination Host is Administratively Prohibited",
                11: "Destination Network Unreachable for Type of Service",
                12: "Destination Host Unreachable for Type of Service",
                13: "Communication Administratively Prohibited",
                14: "Host Precedence Violation",
                15: "Precedence Cutoff in Effect"
            },
            11: {  # Time Exceeded
                0: "Time to Live exceeded in Transit",
                1: "Fragment Reassembly Time Exceeded"
            }
        }
    
        if icmpType in errorMessages and icmpCode in errorMessages[icmpType]:
            return errorMessages[icmpType][icmpCode]
        else:
            return f"Unknown ICMP Type {icmpType} Code {icmpCode}"


# #################################################################################################################### #
# main()                                                                                                               #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #
def main():
    icmpHelperPing = IcmpHelperLibrary()


    # Choose one of the following by uncommenting out the line
    # icmpHelperPing.sendPing("209.233.126.254")
    # icmpHelperPing.sendPing("www.google.com")
    # icmpHelperPing.sendPing("gaia.cs.umass.edu")
    # icmpHelperPing.traceRoute("164.151.129.20")
    # icmpHelperPing.traceRoute("122.56.99.243")
    #icmpHelperPing.traceRoute("www.google.com")
    #icmpHelperPing.traceRoute("www.google.co.jp")
    #icmpHelperPing.traceRoute("www.bbc.co.uk")
    icmpHelperPing.traceRoute("240.0.0.1")

if __name__ == "__main__":
    main()
