from setuptools import setup


setup(name='django-forge',
      version=__import__('forge').__version__,
      author='Justin Bronn',
      author_email='jbronn@gmail.com',
      description='A Django implementation of the Puppet Forge web API.',
      url='https://github.com/jbronn/django-forge',
      download_url='http://pypi.python.org/pypi/django-forge/',
      install_requires=[
        'Django>=1.4',
      ],
      packages=['forge',
                'forge/management',
                'forge/management/commands',],
      package_data={'apache': ['forge/apache'],
                    'templates': ['forge/templates']},
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Apache Software License',
      ],
)
