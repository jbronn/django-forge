from setuptools import setup, find_packages


setup(name='django-forge',
      version=__import__('forge').__version__,
      author='Justin Bronn',
      author_email='jbronn@gmail.com',
      description='A Django implementation of the Puppet Forge API.',
      url='https://github.com/jbronn/django-forge',
      download_url='http://pypi.python.org/pypi/django-forge/',
      install_requires=[
        'Django>=1.8',
        'requests>=2',
        'semantic_version>=2.1.2',
      ],
      packages=find_packages(),
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
