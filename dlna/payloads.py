# coding: UTF-8

class Payloads(object):
  @classmethod
  def set_volume(cls, **kwargs):
    options = {
      'instance_id': 0,
      'channel': 'master',
    }
    options.update(kwargs)
    return {
      'headers': {
        'Content-Type': 'text/xml',
        'SOAPAction': '"urn:schemas-upnp-org:service:RenderingControl:1#SetVolume"',
      },
      'data': """
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:SetVolume xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1">
      <InstanceID>{instance_id}</InstanceID>
      <Channel>{channel}</Channel>
      <DesiredVolume>{volume}</DesiredVolume>
    </u:SetVolume>
  </s:Body>
</s:Envelope>
""".format(**options).strip().encode(),
    }

  
  @classmethod
  def set_volume_db(cls, **kwargs):
    options = {
      'instance_id': 0,
      'channel': 'master',
    }
    options.update(kwargs)
    return {
      'headers': {
        'Content-Type': 'text/xml',
        'SOAPAction': '"urn:schemas-upnp-org:service:RenderingControl:1#SetVolumeDB"',
      },
      'data': """
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:SetVolumeDB xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1">
      <InstanceID>{instance_id}</InstanceID>
      <Channel>{channel}</Channel>
      <DesiredVolume>{volume_db}</DesiredVolume>
    </u:SetVolumeDB>
  </s:Body>
</s:Envelope>
""".format(**options).strip().encode(),
    }

  @classmethod
  def get_volume_db_range(cls, **kwargs):
    options = {
      'instance_id': 0,
      'channel': 'master',
    }
    options.update(kwargs)
    return {
      'headers': {
        'Content-Type': 'text/xml',
        'SOAPAction': '"urn:schemas-upnp-org:service:RenderingControl:1#GetVolumeDBRange"',
      },
      'data': """
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:GetVolumeDBRange xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1">
      <InstanceID>{instance_id}</InstanceID>
      <Channel>{channel}</Channel>
    </u:GetVolumeDBRange>
  </s:Body>
</s:Envelope>
""".format(**options).strip().encode(),
    }

  @classmethod
  def next(cls, **kwargs):
    options = {
      'instance_id': 0
    }
    options.update(kwargs)
    return {
      'headers': {
        'Content-Type': 'text/xml',
        'SOAPAction': '"urn:schemas-upnp-org:service:AVTransport:1#Next"',
      },
      'data': """
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:Next xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
      <InstanceID>{instance_id}</InstanceID>
    </u:Next>
  </s:Body>
</s:Envelope>
""".format(**options).strip().encode(),
    }

  @classmethod
  def pause(cls, **kwargs):
    options = {
      'instance_id': 0
    }
    options.update(kwargs)
    return {
      'headers': {
        'Content-Type': 'text/xml',
        'SOAPAction': '"urn:schemas-upnp-org:service:AVTransport:1#Pause"',
      },
      'data': """
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:Pause xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
      <InstanceID>{instance_id}</InstanceID>
    </u:Pause>
  </s:Body>
</s:Envelope>
""".format(**options).strip().encode(),
    }

  @classmethod
  def stop(cls, **kwargs):
    options = {
      'instance_id': 0
    }
    options.update(kwargs)
    return {
      'headers': {
        'Content-Type': 'text/xml',
        'SOAPAction': '"urn:schemas-upnp-org:service:AVTransport:1#Stop"',
      },
      'data': """
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:Stop xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
      <InstanceID>{instance_id}</InstanceID>
    </u:Stop>
  </s:Body>
</s:Envelope>
""".format(**options).strip().encode(),
    }


  @classmethod
  def play(cls, **kwargs):
    options = {
      'instance_id': 0,
      'speed': 1,
    }
    options.update(kwargs)
    return {
      'headers': {
        'Content-Type': 'text/xml',
        'SOAPAction': '"urn:schemas-upnp-org:service:AVTransport:1#Play"',
      },
      'data': """
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
      <InstanceID>{instance_id}</InstanceID>
      <Speed>{speed}</Speed>
    </u:Play>
  </s:Body>
</s:Envelope>
""".format(**options).strip().encode(),
    }

  @classmethod
  def set_url(self, **kwargs):
    options = {
      'instance_id': 0,
      'metadata': '',
    }
    options.update(kwargs)
    return {
      'headers': {
        'Content-Type': 'text/xml',
        'SOAPAction': '"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"',
      },
      'data': """
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
      <InstanceID>{instance_id}</InstanceID>
      <CurrentURI>{url}</CurrentURI>
      <CurrentURIMetaData>{metadata}</CurrentURIMetaData>
    </u:SetAVTransportURI>
  </s:Body>
</s:Envelope>
""".format(**options).strip().encode(),
    }

  @classmethod
  def set_next_url(self, **kwargs):
    options = {
      'instance_id': 0,
      'metadata': '',
    }
    options.update(kwargs)
    return {
      'headers': {
        'Content-Type': 'text/xml',
        'SOAPAction': '"urn:schemas-upnp-org:service:AVTransport:1#SetNextAVTransportURI"',
      },
      'data': """
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:SetNextAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
      <InstanceID>{instance_id}</InstanceID>
      <NextURI>{url}</NextURI>
      <NextURIMetaData>{metadata}</NextURIMetaData>
    </u:SetNextAVTransportURI>
  </s:Body>
</s:Envelope>
""".format(**options).strip().encode(),
    }

  
