'''
Tools for writing bind/named zone files.

Created on Jan 7, 2011

@author: Jason Walton
'''

import datetime
import re

_ZONE_FILE_SOA_TIMER_JUSTIFY = 8
_ZONE_FILE_LEFT_COLUMN_WIDTH = 31
_ZONE_FILE_MID_COLUMN_WIDTH = 10

def macAddressToEUI64(macAddress):
    '''Given a MAC Address as a string, generates an EUI-64 identifier for the
    interface ID.
    
    This is handy if you are using autoconfiguration; if you know the MAC
    addresses of your machines, you can generate the interface IDs, and then
    concatonate them with the appropriate global routing prefix and subnet ID,
    or with "fe80::" if you're using link-local addresses.
    
    @param macAddress: the MAC address as a string (e.g. "00:24:01:0f:77:70")
    @return the EUI64 identifier associated with the MAC. (e.g. "0224:01ff:fe0f:7770")
    '''
    macOctets = macAddress.split(":")
    macOctets.insert(3, "fe")
    macOctets.insert(3, "ff")
    macOctets[0] = ("%x" % (int(macOctets[0], 16) | 2)).rjust(2,"0")
    eui64 = (macOctets[0] + macOctets[1] + ":" +
             macOctets[2] + macOctets[3] + ":" +
             macOctets[4] + macOctets[5] + ":" +
             macOctets[6] + macOctets[7]).lower()
    return eui64

def expandIPv6Address(address):
    '''Takes an IPv6 address, and writes it out in the longest form possible.
    
    For example, this would translate:
    
        fe08::1
        
    To:
    
        fe08:0000:0000:0000:0000:0000:0000:0001
        
    This will generate "canonical" IPv6 addresses.
        
    @param address the address to expand.
    @return the passed in address, in the longest possible format.
    '''
    fields = address.split(":")
    answer = ""
    fieldsWritten = 0
    parsedMissingFields = 0
    for field in fields:
        if len(field) == 0 and not parsedMissingFields:
            parsedMissingFields = 1
            specifiedFields = len(fields) - 1
            missingFields = 8 - specifiedFields
            for x in range(missingFields):
                answer += "0000"
                fieldsWritten += 1
                if(fieldsWritten < 8): answer = answer + ":"
        else:
            answer += field.rjust(4, "0")
            fieldsWritten += 1
            if(fieldsWritten < 8): answer = answer + ":"
    return answer

def _isAbsoluteDomainName(name):
    return name.endswith(".")

class MailExchanger:
    '''Defines a mail exchanger
    '''
    def __init__(self, mailHost, priority=1):
        '''
        @param mailHost: the name of the mail exchanger to send mail to.  Note that
          if this is an absolute domain name, it should end in a "." (e.g. "thedreaming.org.")
        @param priority: the priority of this mail exchanger (lower numeric value is
          higher priority.)
        '''
        self._mailHost = mailHost
        self._priority = priority
        
    def getMailHost(self):
        return self._mailHost
    
    def getPriority(self):
        return self._priority

class Host:
    '''A host defines a domain name, and any addresses and other records 
    associated with it.
    '''
    def __init__(self, 
                 name, 
                 addresses = list(), 
                 aliases = list(),
                 mailExchangers = list(),
                 ipv6Addresses = list()):
        '''
        @param name: the hostname for this host.  Can be relative or absolute 
            (absolute must end in ".")
        @param addresses: a list of IPv4 addresses associated with this host.
            (e.g. ["192.168.0.1"])
        @param aliases: aliases for this host (these will become CNAME records).
        @param mailExchangers: a list of mail exchangers for this host.
            (e.g. [MailExchanger("x.org.", 10), MailExchanger("backupmail.x.org.", 20)]
        @param ipv6Addresses: a list of IPv6 addresses associated with this host.
            (e.g. ["fe80::0224:01ff:fe0f:7770"])
        '''
        
        self._name = name
        self._addresses = addresses
        self._aliases = aliases
        self._mailExchangers = mailExchangers
        self._ipv6Addresses = ipv6Addresses
        
    def getName(self):
        '''Returns the name of this Host'''
        return self._name
    
    def getAddresses(self):
        '''Returns the list of IPv4 addresses associate with this Host'''
        return self._addresses
    
    def addAddress(self, address):
        '''Add an IPv4 address to this host'''
        self._addresses.append(address)
    
    def getIPv6Addresses(self):
        '''Returns the list of IPv6 addresses associate with this Host'''
        return self._ipv6Addresses
    
    def addIPv6Address(self, ipv6Address):
        '''Add an IPv6 address to this host'''
        self._ipv6Addresses.append(ipv6Address)
        
    def getAliases(self):
        '''Returns the list of aliases for this Host.'''
        return self._aliases
    
    def addAlias(self, alias):
        '''Add an alias address to this host'''
        self._aliases.append(alias)
        
    def getMailExchangers(self):
        '''Returns the list of mail exchangers for this Host.'''
        return self._mailExchangers
    
    def addMailExchanger(self, mailExchanger):
        self._mailExchangers.append(mailExchanger)

class Zone:
    '''A collection of hosts which can be written out to a zone file'''
    def __init__(self, 
                 zoneName,
                 contactAddress,
                 nameServers,
                 hosts = list(),
                 ttl = "1D",
                 refresh = "2H",
                 retry = "5M",
                 expire = "1W",
                 negativeCacheTtl = "1M"
                 ):
        '''Create a Zone.
        
        @param zoneName: the name of the zone (e.g. "thedreaming.org.")
        @param contactAddress: the email address of the primary contact for the
            zone with the "@" replaced with a "." (e.g. "root.thedreaming.org.")
        @param nameServers: a list of name servers which are authoratative for this zone.
            There must be at least one name server.
        @param hosts: a list of hosts that make up the zone.
        @param ttl defines the duration that a record from this zone may be cached. (e.g. "1D")
        @param refresh how often a secondary will poll the primary server to see if the
            zone file has changed.
        @param retry time between retires if a secondary cannot contact the primary.
        @param expire how long a secondary will treat its zone data as authoratative if
            it cannot contact the primary.
        @param negativeCacheTtl the time a negative result will be cached for. 
        '''
        self._zoneName = zoneName
        self._hosts = hosts
        self._nameServers = nameServers
        self._contactAddress = contactAddress
        self._ttl = ttl
        self._refresh = refresh
        self._retry = retry
        self._expire = expire
        self._negativeCacheTtl = negativeCacheTtl
        

    def writeSOARecord(self, out, serialNumber):
        '''Write out an SOA record for a zone.
        
        @param out: the file to write data to.
        @paramn serialNumber: the serial number to write for the zone.
        '''
        out.write("@".ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + " " +
                  "IN SOA".ljust(_ZONE_FILE_MID_COLUMN_WIDTH) + " " +
                   self._nameServers[0] + " " + self._contactAddress + " (\n")
        out.write("".ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + "    " + serialNumber.ljust(_ZONE_FILE_SOA_TIMER_JUSTIFY) + " ; Serial\n")
        out.write("".ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + "    " + self._refresh.ljust(_ZONE_FILE_SOA_TIMER_JUSTIFY) + " ; Refresh slaves\n")
        out.write("".ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + "    " + self._retry.ljust(_ZONE_FILE_SOA_TIMER_JUSTIFY) + " ; Retry\n")
        out.write("".ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + "    " + self._expire.ljust(_ZONE_FILE_SOA_TIMER_JUSTIFY) + " ; Expire\n")
        out.write("".ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + "    " + self._negativeCacheTtl.ljust(_ZONE_FILE_SOA_TIMER_JUSTIFY) + " ; Negative cache TTL\n")
        out.write("".ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + " )\n")


    def writeNSRecords(self, out):
        '''Write out an NS record for a zone.'''
        for ns in self._nameServers:
            out.write("@".ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + " " + "IN NS".ljust(_ZONE_FILE_MID_COLUMN_WIDTH) + " " + ns + "\n")

    def _generateSerialNumber(self):
        '''Generate a serial number based on the current date.'''
        today = datetime.date.today()
        return str(today.year) + str(today.month).rjust(2, "0") + str(today.day).rjust(2, "0")

    def _writeZoneFileProlog(self, out, serialNumber):
        '''Writes out the TTL, SOA record, and NS records for the current zone.
        
        @param out: the file to write data to.
        @param serialNumber: the serial number to write for the zone.
        '''
        if not serialNumber:
            serialNumber = self._generateSerialNumber()
        out.write("$TTL " + self._ttl + "\n\n")
        self.writeSOARecord(out, serialNumber)
        self.writeNSRecords(out)

    def writeZoneFile(self, 
                      out,
                      serialNumber = ""):
        '''Writes out the zone file for this zone.
        
        @param out: the file to write data to.
        @param serialNumber: the serial number to write for the zone.  If not
            specified, a serial number will be generated based on today's date.
        '''
        self._writeZoneFileProlog(out, serialNumber)
        
        # Write A, AAAA, MX, and CNAME records for every host
        for host in self._hosts:
            for address in host.getAddresses():
                out.write(host.getName().ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + " " +
                          "IN A".ljust(_ZONE_FILE_MID_COLUMN_WIDTH) + " " +
                          address + "\n")
            for address in host.getIPv6Addresses():
                out.write(host.getName().ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + " " +
                          "IN AAAA".ljust(_ZONE_FILE_MID_COLUMN_WIDTH) + " " +
                          address + "\n")
            for mx in host.getMailExchangers():
                out.write(host.getName().ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + " " +
                          "IN MX".ljust(_ZONE_FILE_MID_COLUMN_WIDTH) + " " +
                          str(mx.getPriority()) +  " "  +
                          mx.getMailHost() + "\n")
            for alias in host.getAliases():
                out.write(alias.ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + " " +
                          "IN CNAME".ljust(_ZONE_FILE_MID_COLUMN_WIDTH) + " " +
                          host.getName() + "\n")
            

    def writeReverseZoneFile(self,
                             out,
                             prefix,
                             serialNumber = ""):
        '''Write a reverse-mapping zone file for the given prefix.
        
        @param out the file to write to.
        @param prefix the IPv4 prefix we are writing a file for (e.g. "192.168.0." 
            for "0.192.168.in-addr.arpa")
        @param serialNumber: the serial number to write for the zone.  If not
            specified, a serial number will be generated based on today's date.
        '''
        self._writeZoneFileProlog(out, serialNumber)
        
        if not prefix.endswith("."):
            prefix = prefix + "."
        
        # Write PTR records for all hosts which match the given prefix 
        for host in self._hosts:
            for address in host.getAddresses():
                if address.startswith(prefix):
                    hostname = host.getName()
                    if not _isAbsoluteDomainName(hostname):
                        # Make path absolute
                        hostname = hostname + "." + self._zoneName
                        
                    partialAddress = str(address[len(prefix):])
                    reversedPartialAddress = ".".join(partialAddress.split(".")[::-1])

                    out.write(reversedPartialAddress.ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + " " +
                              "IN PTR".ljust(_ZONE_FILE_MID_COLUMN_WIDTH) + " " +
                              hostname + "\n")

                    
    def writeReverseIPv6ZoneFile(self,
                                 out,
                                 prefix,
                                 serialNumber = ""):
        '''Write a reverse-mapping zone file for the given IPv6 prefix.
        
        @param out the file to write to.
        @param prefix the IPv6 prefix we are writing a file for (e.g. "2.0.0.1." 
            for "1.0.0.2.ip6.arpa")
        @param serialNumber: the serial number to write for the zone.  If not
            specified, a serial number will be generated based on today's date.
        '''
        self._writeZoneFileProlog(out, serialNumber)
        
        if not prefix.endswith("."):
            prefix = prefix + "."

        # Write PTR records for all hosts which match the given netmask 
        for host in self._hosts:
            for address in host.getIPv6Addresses():
                fullAddress = expandIPv6Address(address)
                addressDigits = [x for x in re.sub(':', '', fullAddress)]
                dottedAddress = ".".join(addressDigits)
                if dottedAddress.startswith(prefix):
                    hostname = host.getName()
                    if not _isAbsoluteDomainName(hostname):
                        # Make path absolute
                        hostname = hostname + "." + self._zoneName
                        
                    partialAddress = str(dottedAddress[len(prefix):])
                    reversedPartialAddress = ".".join(partialAddress.split(".")[::-1])
                    
                    out.write(reversedPartialAddress.ljust(_ZONE_FILE_LEFT_COLUMN_WIDTH) + " " +
                              "IN PTR".ljust(_ZONE_FILE_MID_COLUMN_WIDTH) + " " +
                              hostname + "\n")
        

if __name__ == '__main__':
    import sys
    
    # Quick test for Bind9Tools
    hosts = [
        Host("thedreaming.org.", 
             ["192.168.0.1", "209.217.122.208"], 
             aliases = ["www", "ftp", "mail", "tachikoma"], 
             mailExchangers = [MailExchanger("thedreaming.org.")]),
        Host("lucid", ["192.168.0.10"], ipv6Addresses = ["fe80::0224:01ff:fe0f:7770"]),
        Host("mystic", ["192.168.0.11"]),
        Host("renegade.thedreaming.org.", ["192.168.0.12"]),
        Host("www.renegade", ["192.168.0.13"])
    ]
    zone = Zone("thedreaming.org.", "root.thedreaming.org", ["thedreaming.org."], hosts)
    
    zone.writeZoneFile(sys.stdout)
    print "-=-=-=-=-=-"
    zone.writeReverseZoneFile(sys.stdout, "192.168.0.")
    print "-=-=-=-=-=-"
    zone.writeReverseIPv6ZoneFile(sys.stdout, "f.e.8.0.0.0.0.0.")
