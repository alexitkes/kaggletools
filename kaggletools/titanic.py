"""
Functions anlyzing "Titanic" data set, the training set for beginners
in machine learning. See `https://www.kaggle.com/c/titanic` for more
info about the dataset these functions and classes should analyze.

Public functions defined here:

*   extract_title

Classed sefined here:

*   TicketCounter
*   CabinCounter
*   FamilyCorrector
"""

import numpy as np
import pandas as pd
import warnings

def extract_title(data, titles=None):
    """
    Create a title column meaning whether the `data.Name` column
    contains Mr, Mrs, Miss, etc.title. Returns a Series of
    integers indicating the titles. Default mapping is the following.

    *   0 means Mr
    *   1 means Mrs
    *   2 means Miss
    *   3 means Master
    *   4 means rare titles like Dr, Sir, etc.

    This mapping may be customized using the `titles` argument
    (see below).

    Parameters
    ----------
    data : pandas.DataFrame
        The data frame that must contain the 'Name' column containing
        the 'Mr', 'Mrs', etc. title in addition to the name itself.

    titles : list, default ['Mr', 'Mrs', 'Miss', 'Master', 'Rare']
        The list of interesting titles. It must contain the Mr, Mrs,
        Miss, Master and Rare strings and may contain Dr, Military
        and Royal. For every passenger, the returned column will
        contain the integer meaning index of this passenger's title
        in the list.

    Returns
    -------
    pandas.Series
        The list of integers of range 0-4 (or `0` to `len (titles) - 1` if
        `titles` argument given) indicating the titles taken from the name
        column. The series index will be same with that of data argument.

    Raises
    ------
    Exception :
        The Mr, Mrs, Miss and Master title not allowed to return.

    Issues
    ------
    *   If `Rare` title not given as interesting, it may be a good idea
        to use 'Mr', 'Mrs', 'Miss', or 'Master' titles depending on
        gender and age.
    """
    if titles is None:
        titles = ['Mr', 'Mrs', 'Miss', 'Master', 'Rare']
    else:
        warnings.warn("Using non-default title list is still an experimental feature and may change without deprecation")
    if 'Mr' not in titles or 'Mrs' not in titles or 'Miss' not in titles or 'Master' not in titles:
        raise Exception("Must be able to return Mr, Mrs, Miss and Master titles.")
    def _mapper(x):
        if x in ["Mr"]:
            return titles.index("Mr")
        elif x in ["Mrs", "Mme"]:
            return titles.index("Mrs")
        elif x in ["Miss", "Ms", "Mlle"]:
            return titles.index("Miss")
        elif x in ["Master"]:
            return titles.index("Master")
        elif x in ["Dr"] and "Dr" in titles:
            return titles.index("Dr")
        elif x in ["Capt", "Major", "Col"] and "Military" in titles:
            return titles.index("Military")
        elif x in ["Sir", "Count", "Countess"] and "Royal" in titles:
            return titles.index("Royal")
        else:
            return titles.index("Rare")
    return data.Name.str.extract("([A-Za-z]+)\\.", expand=False).map(_mapper)

#
# The functions used to calculate survival of the passenger's family members.
#
class TicketCounter(object):
    """
    The object used to calculate the passengers with same ticket number with
    the specified passenger. It can add the following columns to a data
    frame containing the Titanic data.

    *   TicketCount - the number of passengers with this ticket number.

    *   TicketRate - percent of survived passengers with the specified
        ticket number. It may be calculated in different ways depending
        on the constructor parameters.
    """

    def __init__(self, data, simplified=False, fill_if_not_any_survived=False):
        """
        Initialize the ticket counter.

        Parameters
        ----------
        data : pandas.DataFrame
            The source Titanic dataset. The TicketCount and TicketRate
            columns will be added to it. It must contain the following
            columns:

            *   PassengerId - integer, must be unique
            *   Ticket - string, may have duplicates, no NaNs allowed
            *   Survived - 0, 1 or NaN
            *   Pclass - integer, 1, 2, or 3

        simplified : bool, default False
            If True, just fill TicketRate with 1 or 0 values depending on
            fill_if_not_an_survived parameter. The TicketRate will be filled
            with 0.5 for rows with Ticket value not encountered in other
            rows with known survial.
            If False, TicketRate for every will be filled with mean Survived
            value of all **other** passengers with the same ticket number.
            If there is no other passengers with the same ticket number and
            known Survived value, the mean Survived value for the specified
            Pclass value will be used.

        fill_if_not_any_survived : bool, default False
            Only used if simplified is True. The False value (the default)
            means to fill TicketRate with 1 if all other passengers with
            same ticket number survived (or unknown) and 0 if they all died.
            In all other cases, TicketRate will be set to 0.5. The True value
            leads to a bit obscure behavior that nevertheless caused good
            results in numerous public kernels. The TicketRate will be set
            to 1 if any other passenger with the same ticket survived and to
            0 if no passenger with the same ticket is known to survive and
            at least one is known to die.
        """
        self.data = data
        self.simplified = simplified
        self.fill_if_not_any_survived = fill_if_not_any_survived

    def fill_ticket_rates(self):
        """
        Adds the TicketCount and TicketRate columns to the `self.data` frame
        referring to the `data` argument of the constructor.
        """
        counts = {}
        surv = {}
        died = {}
        for t in self.data.Ticket.unique():
            counts[t] = self.data[self.data.Ticket == t].PassengerId.count()
            surv[t] = self.data[(self.data.Ticket == t) & (self.data.Survived == 1)].Survived.count()
            died[t] = self.data[(self.data.Ticket == t) & (self.data.Survived == 0)].Survived.count()
        self.data["TicketCount"] = self.data.Ticket.map(lambda x: counts[x])
        self.data["TicketRate"] = np.NaN
        for i in self.data.index:
            ticket = self.data.loc[i, "Ticket"]
            pid = self.data.loc[i, "PassengerId"]
            if self.simplified:
                if self.fill_if_not_any_survived:
                    if self.data.loc[(self.data.Ticket == ticket) & (self.data.PassengerId != pid)].Survived.max() == 1.0:
                        self.data.loc[i, "TicketRate"] = 1.0
                    elif self.data.loc[(self.data.Ticket == ticket) & (self.data.PassengerId != pid)].Survived.min() == 0.0:
                        self.data.loc[i, "TicketRate"] = 0.0
                else:
                    if self.data.loc[(self.data.Ticket == ticket) & (self.data.PassengerId != pid)].Survived.min() == 1.0:
                        self.data.loc[i, "TicketRate"] = 1.0
                    elif self.data.loc[(self.data.Ticket == ticket) & (self.data.PassengerId != pid)].Survived.max() == 0.0:
                        self.data.loc[i, "TicketRate"] = 0.0
            else:
                s = surv[self.data.loc[i, "Ticket"]]
                d = died[self.data.loc[i, "Ticket"]]
                if np.isfinite(self.data.loc[i].Survived) and (self.data.loc[i].Survived == 1):
                    s -= 1
                if np.isfinite(self.data.loc[i].Survived) and (self.data.loc[i].Survived == 0):
                    d -= 1
                if s + d:
                    self.data.loc[i, "TicketRate"] = float(s) / float(s + d)
        if self.simplified:
            self.data["TicketRate"] = self.data["TicketRate"].fillna(0.5)
        else:
            for c in self.data.Pclass.unique():
                self.data.loc[self.data.Pclass == c, "TicketRate"] = self.data.loc[self.data.Pclass == c, "TicketRate"].fillna(self.data.loc[(self.data.Pclass == c), "Survived"].mean())

class CabinCounter(object):
    """
    The object used to calculate the passengers with same cabin number with
    the specified passenger. It can add the following columns to a data
    frame containing the Titanic data.

    *   CabinCount - the number of passengers with this cabin number.

    *   CabinRate - percent of survived passengers with the specified
        cabin number. It may be calculated in different ways depending
        on the constructor parameters.
    """

    def __init__(self, data, filler=None, simplified=False):
        """
        Initialize the cabin survival rate counter object.

        Parameters
        ----------
        data : pandas.DataFrame
            The source data frame containing Titanic passengers survival data.
            It must contain the following columns.

            *   PassengerId - integer, a unique identifier of the passenger.

            *   Cabin - a string containing number of the passenger's Cabin,
                may be NaN.

            *   Pclass - integer, must be 1, 2 or 3.

            *   Survived - one or zero, may be NaN.

        filler : pd.Series, optional
            A column to be used as CabinRate values for passengers with no
            cabin number or a unique cabin number. If None given, the 0.5
            constant of median survival grouped by Pclass will be used,
            depending on `simplified` value.

        simplified : boolean, default False
            Specifies the way of filling cabin rate. The True value means
            to fill CabinRate with if all other passengers with same cabin
            number survived, 0 if they all die and 0.5otherwise. If
            `simplified` is False (the default behavior) the mean Survival
            value of other passengers of the same cabin will be used.
            In both cases, the CabinRate value of a passenger is calculated
            by a data frame without this passenger and does not depend on
            his/her own survival value.
        """
        self.data = data
        self.simplified = simplified
        if filler is None:
            if simplified:
                self.filler = pd.Series(0.5, index=data.index)
            else:
                self.filler = pd.Series(np.NaN, index=data.index)
                for c in self.data.Pclass.unique():
                    self.filler.loc[self.data.Pclass == c] = self.data.loc[self.data.Pclass == c, "Survived"].mean()
        else:
            self.filler = filler

    def fill_cabin_rates(self):
        """
        Adds the CabinCount and CabinRate columns to the `self.data` data frame,
        that is a referrence to the `data` parameter of the constructor.
        """
        counts = {}
        surv = {}
        died = {}
        for c in self.data.loc[~self.data.Cabin.isna(), "Cabin"].unique():
            counts[c] = self.data[self.data.Cabin == c].PassengerId.count()
            surv[c] = self.data[(self.data.Cabin == c) & (self.data.Survived == 1)].Survived.count()
            died[c] = self.data[(self.data.Cabin == c) & (self.data.Survived == 0)].Survived.count()
        self.data.loc[self.data.Cabin.isna(), "CabinCount"] = 0
        self.data.loc[~self.data.Cabin.isna(), "CabinCount"] = self. data.loc[~self.data.Cabin.isna(), "Cabin"].map(lambda x: counts[x])
        self.data["CabinRate"] = np.NaN
        for i in self.data.index:
            if not self.data.loc[i, "Cabin"] in counts:
                continue
            cabin = self.data.loc[i, "Cabin"]
            pid = self.data.loc[i, "PassengerId"]
            if self.simplified:
                if self.data.loc[(self.data.Cabin == cabin) & (self.data.PassengerId != pid)].Survived.min() == 1.0:
                    self.data.loc[i, "CabinRate"] = 1.0
                elif self.data.loc[(self.data.Cabin == cabin) & (self.data.PassengerId != pid)].Survived.max() == 0.0:
                    self.data.loc[i, "CabinRate"] = 0.0
            else:
                s = surv[cabin]
                d = died[cabin]
                if np.isfinite(self.data.loc[i].Survived) and (self.data.loc[i].Survived == 1):
                    s -= 1
                if np.isfinite(self.data.loc[i].Survived) and (self.data.loc[i].Survived == 0):
                    d -= 1
                if s + d:
                    self.data.loc[i, "CabinRate"] = float(s) / float(s + d)
        self.data.loc[self.data.CabinRate.isna(), "CabinRate"] = self.filler.loc[self.data.CabinRate.isna()]

class FamilyPredictor(object):
    """
    Object used to add family survival information to Titanic dataset.
    """

    def _new_family(self, i):
        """
        Add a new family group to the `self.families` list and place the passenger
        with index `i` to that group.

        Parameters
        ----------
        i : int
            The index of a passenger that should be added to the new family group.
            Must be a valid index of `self.data` frame that is a referrence
            to the `data` argument of the `self` constructor. Note that this
            function does not add the passenger to the family by itself, it 
            only sets appropriate family parameters (class, port of embarkation,
            etc.) to parameters of this passenger.

        Returns
        -------
        int :
            The index of the new family group. It should then be assinged
            to `self.data.Family[i]` to add the passenger to the new goup.
        """
        idx = len(self.families)
        self.families.loc[idx,'Pclass'] = self.data.loc[i, "Pclass"]
        self.families.loc[idx,'Embarked'] = self.data.loc[i, "Embarked"]
        self.families.loc[idx,'Lastname'] = self.data.loc[i, "Lastname"]
        self.families.loc[idx,'Size'] = 0
        self.families.loc[idx,'Id'] = idx
        return idx

    def _find_family(self, i):
        """
        Looks for a good family group to add the passenger with index `i` to
        may return an existing group, but also may create a new family group.

        Parameters
        ----------
        i : int
            Index of a passenger in `self.data` frame.

        Returns
        -------
        int :
            The index of the family group suitable for the given (by index `i`)
            passenger. May be either an already existing family group or a
            just created family group. The `Family` column for the passenger will
            not be updated, it still should be done separately.
        """
        fams = self.families.loc[(self.families.Pclass == self.data.loc[i, "Pclass"]) & (self.families.Embarked == self.data.loc[i, "Embarked"])]
        if not len(fams):
            return self._new_family(i)
        exact = fams.loc[fams.Lastname == self.data.loc[i, "Lastname"]]
        if len(exact):
            return exact.iloc[0].Id
        if self.data.loc[i, "SecondaryLastname"] == np.NaN:
            return self._new_family(i)
        secondary = fams.loc[fams.Lastname == self.data.loc[i, "SecondaryLastname"]]
        if len(exact):
            return exact.iloc[0].Id
        else:
            return self._new_family(i)

    def _fill_family_ids(self):
        """
        Adds the `Family` column to the `self.data` frame. This column will contain
        the family identifiers assigned to the passengers.
        """
        self.families = pd.DataFrame(columns=['Pclass', 'Embarked', 'Lastname', 'Id', 'Size'])
        self.data["Family"] = np.NaN
        if self.use_fare:
            self.data["Family"] = np.NaN
            fid = 0
            for i in self.data.index:
                f = self.data.loc[i].Fare
                l = self.data.loc[i].Lastname
                if np.isfinite(self.data.loc[i].Family):
                    continue
                self.data.loc[(self.data.Fare == f) & (self.data.Lastname == l), "Family"] = fid
                fid += 1
        else:
            for i in self.data.index:
                # Leave family ID NAN if no family.
                if self.data.loc[i, "SibSp"] == 0 and self.data.loc[i, "Parch"] == 0:
                    continue
                self.data.loc[i, "Family"] = self._find_family(i)
                f = self.data.loc[i, "Family"]
                self.families.loc[self.families.Id == f, "Size"] = self.families.loc[self.families.Id == f, "Size"] + 1
            for f in self.families.index:
                if self.families.loc[f].Size != 1:
                    continue
                fid = self.families.loc[f].Id
                pid = self.data.loc[self.data.Family == fid, "PassengerId"].iloc[0]
                pclass = self.data.loc[self.data.Family == fid, "Pclass"].iloc[0]
                emb = self.data.loc[self.data.Family == fid, "Embarked"].iloc[0]
                second_name = self.data.loc[self.data.Family == fid, "SecondaryLastname"].iloc[0]
                if second_name == np.NaN:
                    continue
                fams = self.families.loc[self.families.Lastname == second_name]
                for fam in fams.index:
                    fam_id = fams.loc[fam].Id
                    c = self.data.loc[self.data.Family == fid, "Family"].count()
                    self.families.loc[self.families.Id == fam_id, "Size"] = self.families.loc[self.families.Id == fam_id, "Size"] + c
                    self.data.loc[self.data.Family == fid, "Family"] = fam_id
                    self.families.loc[f, "Size"] = 0
                    break
                if self.families.loc[f, "Size"] == 0:
                    continue
                if self.data.loc[self.data.PassengerId == pid, "SibSp"].iloc[0] == 0:
                    continue
                if self.data.loc[self.data.PassengerId == pid, "Sex"].iloc[0] != 1:
                    continue
                sisters = self.data.loc[(self.data.SecondaryLastname == second_name) &
                                        (self.data.Sex == 'female') &
                                        (self.data.Pclass == pclass) &
                                        (self.data.Embarked == emb) &
                                        (self.data.PassengerId != pid)]
                if len(sisters) > 0:
                    fam_id = sisters.iloc[0].Family
                    c = self.data.loc[self.data.Family == fid, "Family"].count()
                    self.families.loc[self.families.Id == fam_id, "Size"] = self.families.loc[self.families.Id == fam_id, "Size"] + c
                    self.data.loc[data.Family == fid, "Family"] = fam_id
                    self.families.loc[f, "Size"] = 0

    def __init__(self, data, filler=None, simplified=False, use_fare=False, fill_if_not_any_survived=False):
        """
        Initializes a FamilyPredictor object.

        Parameters
        ----------
        data : pandas.DataFrame
            The source data frame. It must contain the following fields.

            *   Name - string, no NaNs
            *   PassengerId - integer, must be unique.
            *   Pclass - integer, 1, 2 or 3 with no NaNs
            *   Parch - non-negative integer
            *   SibSp - non-negative integer
            *   Survived - 1, 0 or NaN
            *   Age - float, in years
            *   Fare - float
            *   Sex - string, "male" or "female", in lowercase, no NaNs
            *   Embarked - string, "C", "S" or "Q" in uppercase, no NaNs

            The following columns will be added to it

            *   Lastname - string, extracted from Name
            *   SecondaryLastname - also string extracted from Name
            *   Family - identifier of the family group found for the passenger
            *   FamilyRate - mean survival value for other family members

        filler : pandas.Series, optional
            A column to be used as FamilyRate value for lone passengers.

        simplified : boolean, default False
            Whether to use the simplified method of filling the family rates
            by default, the "FamilyRate" field will be filled with the mean
            Survived value of other members of the same family (the `filler`
            column will be used for lone passengers of if survival of all
            other family members is unknown). If this field is True, the
            FamilyRate field will be filled with 1 if all other passengers
            of this family survived and 0 if they all died.
            This behavior can be modified by `fill_if_not_any_survived` option.

        use_fare : boolean, default False
            Whether to use the simplified (and possibly more reliable) method
            of finding kins. It assumes all non-alone passengers with same
            lastname and fare fields belong to the same family.

        fill_if_not_any_survived : boolean, default False
            Use a quite obscure but experimetally proved effective method of
            calculating survival rate. In this case the survival rate is
            set to 1 if at least one other family member survived and to 0
            if no family members known to survive and at least one is known
            to die. This way is not written by me. I saw it in many public
            kernels at Kaggle, e. g. the kernel
            `https://www.kaggle.com/konstantinmasich/titanic-0-82-0-83`
            by Konstantin,
            `https://www.kaggle.com/shunjiangxu/blood-is-thicker-than-water-friendship-forever`
            by S.Xu,
            `https://www.kaggle.com/danspace/titanic-knn`
            by Diane Yuan and a number of other kernels.
        """
        self.data = data
        self.simplified = simplified
        self.use_fare = use_fare
        self.fill_if_not_any_survived = fill_if_not_any_survived
        if 'Lastname' not in list(self.data.columns):
            self.data['Lastname'] = self.data['Name'].apply(lambda x: str.split(x, ",")[0])
        if 'SecondaryLastname' not in list(self.data.columns):
            self.data['SecondaryLastname'] = self.data.Name.str.extract("([A-Za-z'-]+)\\)$", expand=False)
            self.data['SecondaryLastname'] = self.data['SecondaryLastname'].fillna(self.data.Lastname.str.extract("^[A-Za-z]+-([A-Za-z]+)$", expand=False))
        if filler is None:
            if simplified:
                self.filler = pd.Series(0.5, index=data.index)
            else:
                self.filler = pd.Series(np.NaN, index=data.index)
                for c in self.data.Pclass.unique():
                    self.filler.loc[self.data.Pclass == c] = self.data.loc[self.data.Pclass == c, "Survived"].mean()
        else:
            self.filler = filler

    def fill_family_rates(self):
        """
        Add the "FamilyRate" columns to the `self.data` frame. This column
        contains the survival rate of the other members of the passenger's
        family, calculated as described in the constructor docstring.
        """
        self._fill_family_ids()
        self.data["FamilyRate"] = np.NaN
        for i in self.data.index:
            if self.data.loc[i, "Family"] == np.NaN:
                continue
            fam = self.data.loc[i, "Family"]
            pid = self.data.loc[i, "PassengerId"]
            if self.data.loc[self.data.Family == fam, "PassengerId"].count() == 1:
                continue
            if self.simplified:
                if self.fill_if_not_any_survived:
                    if self.data.loc[(self.data.Family == fam) & (self.data.PassengerId != pid)].Survived.max() == 1.0:
                        self.data.loc[i, "FamilyRate"] = 1.0
                    elif self.data.loc[(self.data.Family == fam) & (self.data.PassengerId != pid)].Survived.min() == 0.0:
                        self.data.loc[i, "FamilyRate"] = 0.0
                else:
                    if self.data.loc[(self.data.Family == fam) & (self.data.PassengerId != pid)].Survived.min() == 1.0:
                        self.data.loc[i, "FamilyRate"] = 1.0
                    elif self.data.loc[(self.data.Family == fam) & (self.data.PassengerId != pid)].Survived.max() == 0.0:
                        self.data.loc[i, "FamilyRate"] = 0.0
            else:
                self.data.loc[i, "FamilyRate"] = self.data.loc[(self.data.Family == fam) & (self.data.PassengerId != pid)].Survived.mean()
        self.data.loc[self.data.FamilyRate.isna(), "FamilyRate"] = self.filler.loc[self.data.FamilyRate.isna()]
        if self.simplified and self.fill_if_not_any_survived:
            self.data.loc[self.data.FamilyRate < 0.75, "FamilyRate"] = self.filler.loc[self.data.FamilyRate < 0.75]
